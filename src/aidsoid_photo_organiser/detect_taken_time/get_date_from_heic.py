# Copyright (c) 2026 Alexey Doroshenko <aidsoid@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later OR Commercial
# See LICENSE and COMMERCIAL_LICENSE.md for details.

"""Retrieve capture date from HEIC/HEIF files using Pillow with pi_heif extension."""

import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


def get_date_from_heic(file_path: Path) -> datetime | None:
    """
    Retrieve the capture date from HEIC/HEIF files using the Pillow library with pi_heif extension.

    It extracts EXIF metadata (DateTimeOriginal tag) from the HEIC file.

    :param file_path: Path to the HEIC/HEIF image file.
    :return: The extracted date as a datetime object, or None if not available.
    """
    try:
        from pi_heif import register_heif_opener
        from PIL import Image

        # Register HEIF format with Pillow
        register_heif_opener()

        with Image.open(file_path) as img:
            exif_data = img.getexif()
            # Tag 36867 is 'DateTimeOriginal' in the Exif sub-IFD (0x8769)
            exif_ifd = exif_data.get_ifd(0x8769)
            date_str = exif_ifd.get(36867)
            if date_str:
                # Convert the date string to a datetime object
                return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
    except ImportError as e:
        logger.warning(f'⚠️ Required libraries not installed: {e}')
    except Exception as e:
        logger.warning(f'⚠️ Error reading EXIF data from HEIC file: {e}')
    return None
