# Copyright (c) 2026 Alexey Doroshenko <aidsoid@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later OR Commercial
# See LICENSE and COMMERCIAL_LICENSE.md for details.

"""Utilities for counting files and logging file statistics."""

import logging
from pathlib import Path
from typing import Any

from .constants import IGNORED_DIRS, LOG_SEPARATOR

logger = logging.getLogger(__name__)


def log_count_files(stats: dict[str, dict]) -> None:
    """
    Log detailed statistics about files in a directory.

    :param stats: A dictionary containing file statistics, including total counts and sizes
                  for photos, videos, and other file types.
    """
    logger.info(LOG_SEPARATOR)
    logger.info(f'📊 File statistics for {stats["dir"]}:')
    logger.info(f'Total files: {stats["total_files"]} ({stats["total_size"]} bytes)')
    logger.info(f'Photos: {stats["total_photos"]} ({stats["total_photos_size"]} bytes) - {stats["photo_files"]}')
    logger.info(f'Videos: {stats["total_videos"]} ({stats["total_videos_size"]} bytes) - {stats["video_files"]}')
    logger.info(f'Other: {stats["total_other"]} ({stats["total_other_size"]} bytes) - {stats["other_files"]}')
    logger.info(LOG_SEPARATOR + '\n')


def count_files(input_dir: Path, valid_photo_extensions: set[str], valid_video_extensions: set[str]) -> dict[str, Any]:
    """
    Recursively count and categorize files in a directory.

    Categorizes files as photos, videos, or others based on file extensions.
    Calculates the total count and size for each category.

    :param input_dir: The directory to scan for files.
    :param valid_photo_extensions: Set of valid photo file extensions.
    :param valid_video_extensions: Set of valid video file extensions.
    :return: A dictionary with detailed statistics about files in the directory.
    """
    total_files = 0
    total_size = 0
    photo_files = {ext: 0 for ext in valid_photo_extensions}
    video_files = {ext: 0 for ext in valid_video_extensions}
    other_files = {}
    total_photos = 0
    total_videos = 0
    total_other = 0
    total_photos_size = 0
    total_videos_size = 0
    total_other_size = 0

    for file_path in input_dir.rglob('*'):
        # skip directories and files within @eaDir directories
        if IGNORED_DIRS & set(file_path.parts):
            logger.debug(f'Skipping {file_path} (inside @eaDir directory)')
            continue

        if file_path.is_file():
            total_files += 1
            file_size = file_path.stat().st_size
            total_size += file_size
            ext = file_path.suffix.lower()

            if ext in valid_photo_extensions:
                photo_files[ext] += 1
                total_photos += 1
                total_photos_size += file_size
            elif ext in valid_video_extensions:
                video_files[ext] += 1
                total_videos += 1
                total_videos_size += file_size
            else:
                other_files[ext] = other_files.get(ext, 0) + 1
                total_other += 1
                total_other_size += file_size

    stats = {
        'dir': input_dir,
        'total_files': total_files,
        'total_size': total_size,
        'total_photos': total_photos,
        'total_photos_size': total_photos_size,
        'photo_files': photo_files,
        'total_videos': total_videos,
        'total_videos_size': total_videos_size,
        'video_files': video_files,
        'total_other': total_other,
        'total_other_size': total_other_size,
        'other_files': other_files,
    }
    log_count_files(stats)

    return stats
