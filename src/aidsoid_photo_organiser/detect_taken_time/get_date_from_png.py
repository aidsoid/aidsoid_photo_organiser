# Copyright (c) 2026 Alexey Doroshenko <aidsoid@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later OR Commercial
# See LICENSE and COMMERCIAL_LICENSE.md for details.

"""Retrieve capture date from PNG files using Pillow's EXIF support (eXIf chunk)."""

import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


def get_date_from_png(file_path: Path) -> datetime | None:
    """
    Retrieve the capture date from PNG files using the Pillow library.

    PNG files may contain EXIF metadata via the eXIf chunk (PNG 1.5+).
    This function extracts the DateTimeOriginal tag from the EXIF sub-IFD.

    :param file_path: Path to the PNG image file.
    :return: The extracted date as a datetime object, or None if not available.
    """
    try:
        from PIL import Image

        with Image.open(file_path) as img:
            exif_data = img.getexif()
            if not exif_data:
                return None
            # Tag 36867 is 'DateTimeOriginal' in the Exif sub-IFD (0x8769)
            exif_ifd = exif_data.get_ifd(0x8769)
            date_str = exif_ifd.get(36867)
            if date_str:
                return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
    except ImportError as e:
        logger.warning(f'⚠️ Pillow library not installed: {e}')
    except Exception as e:
        logger.warning(f'⚠️ Error reading EXIF data from PNG file: {e}')
    return None
