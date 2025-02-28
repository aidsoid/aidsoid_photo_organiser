# Copyright (c) 2026 Alexey Doroshenko <aidsoid@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later OR Commercial
# See LICENSE and COMMERCIAL_LICENSE.md for details.

"""Retrieve capture date from EXIF metadata of photo files (JPG, JPEG, CR2)."""

import logging
from datetime import datetime
from pathlib import Path

import exifread

logger = logging.getLogger(__name__)


def get_date_from_exif(file_path: Path) -> datetime | None:
    """
    Retrieve the date from EXIF metadata of a photo file.

    The function extracts the "EXIF DateTimeOriginal" tag to determine the original capture date.

    :param file_path: Path to the image file with EXIF metadata.
    :return: The extracted date as a datetime object, or None if not available.
    """
    try:
        with open(file_path, 'rb') as f:
            tags = exifread.process_file(f, stop_tag='EXIF DateTimeOriginal')
            if 'EXIF DateTimeOriginal' in tags:
                return datetime.strptime(str(tags['EXIF DateTimeOriginal']), '%Y:%m:%d %H:%M:%S')
    except Exception as e:
        logger.warning(f'⚠️ Unable to read EXIF data for {file_path} - {e}')
    return None
