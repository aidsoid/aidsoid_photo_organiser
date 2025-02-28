# Copyright (c) 2026 Alexey Doroshenko <aidsoid@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later OR Commercial
# See LICENSE and COMMERCIAL_LICENSE.md for details.

"""Detect capture/taken time from media files and supplemental metadata."""

import logging
from datetime import datetime
from pathlib import Path

from .get_date_from_exif import get_date_from_exif
from .get_date_from_ffprobe import get_date_from_ffprobe
from .get_date_from_filename import extract_datetime_from_filename
from .get_date_from_heic import get_date_from_heic
from .get_date_from_json import get_date_from_json
from .get_date_from_mkv import get_date_from_mkv
from .get_date_from_mp4_atoms import get_date_from_mp4_atoms
from .get_date_from_png import get_date_from_png

logger = logging.getLogger(__name__)

# Unix epoch (1970-01-01 00:00:00) is a common sentinel value meaning "date unknown"
_UNIX_EPOCH = datetime(1970, 1, 1, 0, 0, 0)


def detect_taken_time(file_path: Path) -> datetime | None:
    """
    Universal function for detecting photo or video 'taken time'.

    1. JSON Metadata: Attempts to read the creation date from a supplemental JSON file.
    2.  - EXIF Metadata: Extracts the date from EXIF data for supported photo formats (.jpg, .jpeg, .cr2).
        - HEIC/HEIF Metadata: Reads the capture date from HEIC files using Pillow.
        - Video Metadata: Uses ffprobe to determine the creation date of video files.
    3. Filename: Attempts to extract date/time patterns from the filename.

    :param file_path: Path to the media file.
    :return: The detected 'taken time' as a datetime object, or None if no date could be determined.
    """
    # 1. Trying to get taken time from JSON metadata
    taken_time = get_date_from_json(file_path)
    if _is_valid_taken_time(taken_time, file_path):
        return taken_time

    # 2. Trying to get taken time from file itself (EXIF metadata, HEIC metadata, etc.)
    ext = file_path.suffix.lower()
    # Photo formats with EXIF support
    if ext in {'.jpg', '.jpeg', '.cr2'}:
        taken_time = get_date_from_exif(file_path)
        if _is_valid_taken_time(taken_time, file_path):
            return taken_time
    # HEIC/HEIF photo formats
    elif ext in {'.heic', '.heif'}:
        taken_time = get_date_from_heic(file_path)
        if _is_valid_taken_time(taken_time, file_path):
            return taken_time
    # Video formats
    elif ext in {'.mp4', '.m4v', '.mov', '.mkv'}:
        # Primary: ffprobe via ffmpeg-python (requires ffprobe binary)
        taken_time = get_date_from_ffprobe(file_path)
        # Fallback 1: MP4 atoms parser for MP4/MOV containers (.mp4, .m4v, .mov)
        if not _is_valid_taken_time(taken_time, file_path) and ext in {'.mp4', '.m4v', '.mov'}:
            taken_time = get_date_from_mp4_atoms(file_path)
        # Fallback 2: MKV EBML parser for Matroska files (.mkv)
        elif not _is_valid_taken_time(taken_time, file_path) and ext == '.mkv':
            taken_time = get_date_from_mkv(file_path)
        if _is_valid_taken_time(taken_time, file_path):
            return taken_time
    # Video formats without metadata support
    elif ext in {'.avi', '.hevc', '.mp'}:
        pass
    # PNG files (may contain EXIF via eXIf chunk)
    elif ext == '.png':
        taken_time = get_date_from_png(file_path)
        if _is_valid_taken_time(taken_time, file_path):
            return taken_time
    # Image formats without EXIF support
    elif ext == '.gif':
        pass

    # 3. Trying to get taken time from filename
    taken_time = extract_datetime_from_filename(file_path)
    if _is_valid_taken_time(taken_time, file_path):
        return taken_time

    # 4. Date could not be detected from any source
    return None


def _is_valid_taken_time(taken_time: datetime | None, file_path: Path) -> bool:
    """Check that a detected date is a real capture date, not a sentinel value."""
    if taken_time is None:
        return False
    if taken_time.replace(tzinfo=None) == _UNIX_EPOCH:
        logger.debug(f'Ignoring Unix epoch date for "{file_path}" (sentinel for unknown date)')
        return False
    return True
