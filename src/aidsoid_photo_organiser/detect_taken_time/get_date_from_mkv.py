# Copyright (c) 2026 Alexey Doroshenko <aidsoid@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later OR Commercial
# See LICENSE and COMMERCIAL_LICENSE.md for details.

"""
MKV (EBML) parsing helpers.

Contains a pure-Python lightweight parser to extract the DateUTC element from
Matroska (MKV) files.
"""

import logging
from datetime import datetime, timedelta, timezone
from io import BytesIO
from pathlib import Path

logger = logging.getLogger(__name__)


def _read_ebml_vint(data: BytesIO) -> int | None:
    """
    Read EBML Variable-Size Integer (VINT).

    VINT format: leading zeros + marker bit (1) + data bits
    Examples: 1xxxxxxx (1 byte), 01xxxxxx xxxxxxxx (2 bytes)
    """
    # Read first byte to determine VINT length
    first = data.read(1)
    if not first:
        return None
    fb = first[0]

    # Find the position of the marker bit (first 1 bit)
    mask = 0x80  # Start with most significant bit: 10000000
    length = 1
    while length <= 8 and not (fb & mask):
        mask >>= 1  # Shift right to check next bit
        length += 1
    if length > 8:
        return None

    # Extract data bits from first byte (exclude width bits and marker)
    # Example: for 1 byte (1xxxxxxx), mask is 0x7F to get 7 data bits
    value = fb & (0xFF >> length)

    # Read remaining bytes and combine into final value
    if length - 1 > 0:
        rest = data.read(length - 1)
        if len(rest) < (length - 1):
            return None
        for b in rest:
            value = (value << 8) | b  # Shift left and add next byte
    return value


def get_date_from_mkv(file_path: Path) -> datetime | None:
    """
    Parse Matroska (MKV) EBML headers and extract the DateUTC element.

    The DateUTC element is located in Segment->Info->DateUTC (element id 0x4461).
    DateUTC is stored as an int (signed big-endian) representing nanoseconds
    since 2001-01-01T00:00:00 UTC.
    """
    # EBML metadata headers (Segment→Info→DateUTC) are at the start of the
    # file.  Reading 1 MB is more than enough; avoids loading multi-GB files.
    read_limit = 1_048_576  # 1 MB

    try:
        with open(file_path, 'rb') as f:
            data = f.read(read_limit)

        # Step 1: Find the Segment element (root container)
        # Segment Element ID: 0x18538067
        seg_id = b'\x18\x53\x80\x67'
        idx = data.find(seg_id)
        if idx == -1:
            return None

        # Step 2: Read Segment size (VINT encoded) and extract its payload
        bio = BytesIO(data[idx + len(seg_id) :])
        seg_size = _read_ebml_vint(bio)
        if seg_size is None:
            return None
        seg_payload = bio.read(seg_size)
        if not seg_payload:
            return None

        # Step 3: Find the Info element inside Segment
        # Info Element ID: 0x1549A966
        info_id = b'\x15\x49\xa9\x66'
        info_idx = seg_payload.find(info_id)
        if info_idx == -1:
            return None

        # Step 4: Read Info size and extract its payload
        bio_info = BytesIO(seg_payload[info_idx + len(info_id) :])
        info_size = _read_ebml_vint(bio_info)
        if info_size is None:
            return None
        info_payload = bio_info.read(info_size)
        if not info_payload:
            return None

        # Step 5: Find DateUTC element inside Info
        # DateUTC Element ID: 0x4461
        date_id = b'\x44\x61'
        didx = info_payload.find(date_id)
        if didx == -1:
            return None

        # Step 6: Read DateUTC size and value
        bio_date = BytesIO(info_payload[didx + len(date_id) :])
        date_size = _read_ebml_vint(bio_date)
        if date_size is None:
            return None
        date_bytes = bio_date.read(date_size)
        if not date_bytes:
            return None

        # Step 7: Convert nanoseconds since 2001-01-01 to datetime
        # Pad to 8 bytes if needed (for proper signed int conversion)
        if len(date_bytes) < 8:
            date_bytes = date_bytes.rjust(8, b'\x00')
        ns = int.from_bytes(date_bytes, 'big', signed=True)
        epoch = datetime(2001, 1, 1, tzinfo=timezone.utc)
        return epoch + timedelta(seconds=ns / 1_000_000_000)
    except Exception as e:
        logger.warning(f'⚠️ MKV parser failed for {file_path} - {e}')
    return None
