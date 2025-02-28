# Copyright (c) 2026 Alexey Doroshenko <aidsoid@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later OR Commercial
# See LICENSE and COMMERCIAL_LICENSE.md for details.

"""Retrieve capture date from Google Takeout supplemental metadata JSON files."""

import json
import logging
from datetime import UTC, datetime
from pathlib import Path

logger = logging.getLogger(__name__)


def _get_expected_metadata_filename(file_path: Path) -> str:
    """
    Generate the expected metadata filename based on Google Takeout's naming convention.

    Google Takeout naming algorithm:
    1. Takes the original filename (WITH extension)
    2. Appends ".supplemental-metadata" suffix
    3. Truncates to 46 characters
    4. Appends ".json" extension

    Examples:
        - Original: "DSC_0001_15.JPG"
          With suffix: "DSC_0001_15.JPG.supplemental-metadata"
          Truncated to 46 chars: "DSC_0001_15.JPG.supplemental-metadata" (36 chars)
          Result: "DSC_0001_15.JPG.supplemental-metadata.json"

        - Original: "00100dPORTRAIT_00100_BURST20190825170724237_COV.jpg"
          With suffix: "00100dPORTRAIT_00100_BURST20190825170724237_COV.jpg.supplemental-metadata"
          Truncated to 46 chars: "00100dPORTRAIT_00100_BURST20190825170724237_CO"
          Result: "00100dPORTRAIT_00100_BURST20190825170724237_CO.json"

    :param file_path: The path to the media file.
    :return: The expected metadata filename.

    """
    file_name = file_path.name  # name WITH extension
    # Add .supplemental-metadata suffix, then truncate to 46 characters
    with_suffix = f'{file_name}.supplemental-metadata'
    truncated_name = with_suffix[:46]
    return f'{truncated_name}.json'


def find_supplemental_metadata_json(file_path: Path) -> Path | None:
    """
    Search for a supplemental metadata JSON file associated with the given file.

    The function:
    1. Computes the expected metadata filename based on Google Takeout's naming convention
    2. Checks if the file exists in the same directory

    Google Takeout naming pattern:
        - Takes the original filename (WITH extension)
        - Appends ".supplemental-metadata" suffix
        - Truncates to 46 characters
        - Appends ".json"

    Example:
        - photo.jpg → photo.jpg.supplemental-metadata.json
        - 00100dPORTRAIT_00100_BURST20190825170724237_COV.jpg
          → 00100dPORTRAIT_00100_BURST20190825170724237_CO.json

    :param file_path: The path to the original media file.
    :return: The path to the found metadata file, or None if no matching file is found.

    """
    expected_metadata_filename = _get_expected_metadata_filename(file_path)
    metadata_file = file_path.parent / expected_metadata_filename

    if metadata_file.exists():
        return metadata_file

    return None


def get_date_from_json(file_path: Path) -> datetime | None:
    """
    Retrieve the date from a supplemental JSON file if available.

    The JSON file is expected to have a "photoTakenTime" field with a "timestamp" value.
    Example filename pattern: "image.jpg.supplemental-metadata.json"

    :param file_path: Path to the original media file.
    :return: The extracted date as a datetime object, or None if not available.
    """
    metadata_file = find_supplemental_metadata_json(file_path)
    if metadata_file:
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                if 'photoTakenTime' in metadata and 'timestamp' in metadata['photoTakenTime']:
                    return datetime.fromtimestamp(int(metadata['photoTakenTime']['timestamp']), UTC)
        except Exception as e:
            logger.warning(f'⚠️ Unable to read metadata file {metadata_file} - {e}')
    return None
