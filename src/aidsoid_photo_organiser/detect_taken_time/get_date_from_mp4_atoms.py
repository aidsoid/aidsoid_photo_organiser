# Copyright (c) 2026 Alexey Doroshenko <aidsoid@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later OR Commercial
# See LICENSE and COMMERCIAL_LICENSE.md for details.

"""
MP4/MOV atom parsing helper.

Contains a pure-Python parser to extract creation time from the 'mvhd' atom
in ISO-BMFF (MP4/MOV/M4V) files.
"""

import logging
from datetime import datetime, timedelta, timezone
from io import BytesIO
from pathlib import Path

logger = logging.getLogger(__name__)


def get_date_from_mp4_atoms(file_path: Path) -> datetime | None:
    """
    Retrieve creation time from MP4/MOV container by parsing 'mvhd' atom.

    Per ISO/IEC 14496-12 (ISO Base Media File Format) specification:
    - Files consist of nested boxes (atoms) with [size][type][data] structure
    - 'moov' box contains movie metadata
    - 'mvhd' box inside 'moov' contains creation time

    Returns datetime in UTC when available.
    """
    try:
        with open(file_path, 'rb') as f:
            # Iterate through top-level boxes/atoms in the file
            while True:
                hdr = f.read(8)
                if len(hdr) < 8:
                    break
                # Box header: 4 bytes size (big-endian) + 4 bytes type (ASCII)
                size = int.from_bytes(hdr[0:4], 'big')
                typ = hdr[4:8].decode('latin-1')

                # Handle extended size: size==1 means actual size is in next 8 bytes
                if size == 1:
                    largesize_bytes = f.read(8)
                    if len(largesize_bytes) < 8:
                        break
                    size = int.from_bytes(largesize_bytes, 'big')
                    header_size = 16
                else:
                    header_size = 8

                if size < header_size:
                    break

                # Found 'moov' (movie metadata container) - search inside for 'mvhd'
                if typ == 'moov':
                    moov_data = f.read(size - header_size)
                    bio = BytesIO(moov_data)
                    # Parse nested boxes inside 'moov'
                    while True:
                        hh = bio.read(8)
                        if len(hh) < 8:
                            break
                        sz = int.from_bytes(hh[0:4], 'big')
                        tp = hh[4:8].decode('latin-1')
                        # Handle extended size for nested boxes
                        if sz == 1:
                            larg = bio.read(8)
                            if len(larg) < 8:
                                break
                            sz = int.from_bytes(larg, 'big')
                            inner_header = 16
                        else:
                            inner_header = 8

                        content = bio.read(sz - inner_header) if sz > inner_header else b''

                        # Found 'mvhd' (movie header) - extract creation time
                        if tp == 'mvhd':
                            if len(content) < 8:
                                break
                            # mvhd structure: version(1) + flags(3) + creation_time(4 or 8)
                            version = content[0]
                            if version == 1:
                                # Version 1: 64-bit timestamps (bytes 4-12)
                                if len(content) < 12:
                                    break
                                creation = int.from_bytes(content[4:12], 'big')
                            else:
                                # Version 0: 32-bit timestamps (bytes 4-8)
                                creation = int.from_bytes(content[4:8], 'big')

                            if creation == 0:
                                return None

                            # QuickTime epoch: seconds since midnight, January 1, 1904 UTC
                            epoch = datetime(1904, 1, 1, tzinfo=timezone.utc)
                            return epoch + timedelta(seconds=creation)

                    break
                else:
                    # Skip non-moov boxes
                    to_skip = size - header_size
                    f.seek(to_skip, 1)
    except Exception as e:
        logger.warning(f'⚠️ MP4 atom parser failed for {file_path} - {e}')
    return None
