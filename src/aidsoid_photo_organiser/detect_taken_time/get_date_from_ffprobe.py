# Copyright (c) 2026 Alexey Doroshenko <aidsoid@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later OR Commercial
# See LICENSE and COMMERCIAL_LICENSE.md for details.

"""Retrieve creation date from video metadata using ffprobe (ffmpeg-python)."""

import logging
import shutil
from datetime import datetime
from functools import lru_cache
from pathlib import Path

import ffmpeg

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _is_ffprobe_available() -> bool:
    """Check once whether ffprobe is available in PATH (result is cached)."""
    available = shutil.which('ffprobe') is not None
    if not available:
        logger.warning(
            '⚠️ ffprobe not found in PATH; video metadata extraction via ffprobe will be skipped. '
            'Install ffmpeg or ensure ffprobe is in PATH.'
        )
    return available


def ffprobe_time_str_to_datetime(time_str: str) -> datetime:
    """Convert the creation time (extracted by ffprobe) to a datetime object."""
    return datetime.fromisoformat(time_str.replace('Z', '+00:00'))


def get_date_from_ffprobe(file_path: Path) -> datetime | None:
    """
    Retrieve the creation date from video metadata using the ffmpeg-python library.

    It extracts the 'creation_time' from the format tags (container metadata).

    :param file_path: Path to the video file.
    :return: The extracted date as a datetime object, or None if not available.
    """
    if not _is_ffprobe_available():
        return None

    try:
        # Retrieve metadata from the video file using ffmpeg.probe
        probe = ffmpeg.probe(str(file_path), show_entries='format_tags=creation_time')

        # Extract 'creation_time' from metadata
        creation_time = probe.get('format', {}).get('tags', {}).get('creation_time')

        if creation_time:
            # Convert the creation time to a datetime object
            return ffprobe_time_str_to_datetime(creation_time)

        logger.debug(f"⚠️ No 'creation_time' found in metadata for {file_path}.")

    except FileNotFoundError:
        logger.warning(f'⚠️ ffprobe not found; metadata extraction skipped for {file_path}. Install ffmpeg.')
    except ffmpeg.Error as e:
        logger.warning(f'⚠️ Unable to retrieve video metadata for {file_path} - {e.stderr.decode()}')
    except Exception as e:
        logger.warning(f'⚠️ An unexpected error occurred while processing {file_path} - {e}')

    return None
