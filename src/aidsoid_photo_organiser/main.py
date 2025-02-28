# Copyright (c) 2026 Alexey Doroshenko <aidsoid@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later OR Commercial
# See LICENSE and COMMERCIAL_LICENSE.md for details.

"""CLI for organizing photos and videos by capture date."""

import argparse
import json
import logging
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path

from .configure_logger import configure_root_logger, configure_third_party_loggers
from .constants import (
    IGNORED_DIRS,
    LOG_SEPARATOR,
    VALID_EXTENSIONS,
    VALID_PHOTO_EXTENSIONS,
    VALID_VIDEO_EXTENSIONS,
)
from .count_files import count_files
from .detect_taken_time import detect_taken_time, find_supplemental_metadata_json
from .file_operations import (
    CreateHardlinkOrCopyFileError,
    are_files_identical,
    copy_file_or_create_hardlink,
)
from .replicate_files import replicate_files_with_structure
from .set_file_timestamps import set_file_timestamps

logger = logging.getLogger(__name__)


class ProcessFileError(Exception):
    """Raised when processing a file fails."""

    pass


def _is_supplemental_metadata_json(file_path: Path) -> bool:
    """
    Check if a file is a supplemental metadata JSON file from Google Photos.

    Strategy:
    1. Check if file has .json extension
    2. Quick check: look for .supplemental pattern in filename (handles all truncation variants)
    3. Content check: verify JSON contains 'title' field (present in all Google Photos metadata)

    The .supplemental pattern handles all Google Takeout truncations:
        - .supplemental-metadata.json
        - .supplemental-metadat.json
        - .supplemental-meta.json
        - etc.

    :param file_path: The file path to check.
    :return: True if the file is Google Photos metadata, False otherwise.
    """
    # Step 1: Check if file has .json extension
    if file_path.suffix.lower() != '.json':
        return False

    filename = file_path.name

    # Step 2: Quick check for truncated Google Takeout patterns in filename (fast, no file read needed)
    # Checks for ".supplemental-" pattern which appears in all Google Takeout metadata variants:
    # .supplemental-metadata.json → contains ".supplemental-"
    # .supplemental-meta.json → contains ".supplemental-"
    # .supplemental-m.json → contains ".supplemental-"
    # etc.
    if '.supplemental-' in filename.lower():
        return True

    # Step 3: Fallback - check JSON content for 'title' field (Google Photos indicator)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return 'title' in data
    except (json.JSONDecodeError, OSError):
        return False


def copy_supplemental_metadata_json(
    file_path: Path, target_dir: Path, unique_id: str | None = None, use_hardlinks: bool = False
) -> dict:
    """
    Handle copying of a supplemental metadata JSON file.

    :param file_path: Path to the original media file.
    :param target_dir: The directory where the metadata file should be placed.
    :param unique_id: Optional unique identifier to append to the filename if renaming is required.
    :param use_hardlinks: If True, creates a hardlink instead of copying the file. Defaults to False.
    :return: A dict with metadata_path (Optional[Path]) and status (str):
             "copied", "duplicate", "conflict", "not_found", or "error".
    """
    metadata_file_path = find_supplemental_metadata_json(file_path)

    if not metadata_file_path:
        return {'metadata_path': None, 'status': 'not_found'}

    target_file_path = target_dir / metadata_file_path.name
    if unique_id:
        unique_metadata_name = f'{metadata_file_path.stem}_{unique_id}.json'
        target_file_path = target_dir / unique_metadata_name
        logger.warning(f'🔄 Renaming metadata file to "{unique_metadata_name}".')

    if target_file_path.exists():
        try:
            is_duplicate = are_files_identical(file_1=metadata_file_path, file_2=target_file_path)
        except OSError as e:
            logger.error(
                f'🛑 Target file {target_file_path} already exists. '
                f'Error while trying to detect if files are duplicates: {e}. '
                f'Skipping copy. You should check this file manually in the source directory.'
            )
            return {'metadata_path': metadata_file_path, 'status': 'error'}

        if is_duplicate:
            logger.warning(
                f'📄 Skip copying metadata duplicate:\n  from: "{metadata_file_path}"\n  to: "{target_file_path}"'
            )
            return {'metadata_path': metadata_file_path, 'status': 'duplicate'}
        else:
            logger.warning(
                f'🔀 Metadata conflict. Skipping copy (will be replicated separately):\n'
                f'  source: "{metadata_file_path}"\n'
                f'  target: "{target_file_path}" (already exists with different content)'
            )
            return {'metadata_path': metadata_file_path, 'status': 'conflict'}
    else:
        copy_file_or_create_hardlink(
            src=metadata_file_path, dst=target_file_path, use_hardlinks=use_hardlinks, is_metadata_file=True
        )
        return {'metadata_path': metadata_file_path, 'status': 'copied'}


def proceed_file(file_path: Path, output_dir: Path, use_hardlinks: bool) -> dict:
    """
    Process a file by organizing it into a directory structure by year and month, including handling metadata.

    :param file_path: Path to the input file to process.
    :param output_dir: Base output directory where files should be organized.
    :param use_hardlinks: If True, creates a hardlink instead of copying the file.
    :return: A dict with media_status ("copied" or "duplicate"),
             metadata_path (Optional[Path]), and metadata_status (str).
    :raises ProcessFileError:
    """
    taken_time = detect_taken_time(file_path)
    if taken_time:
        year_dir = output_dir / str(taken_time.year)
        month_dir = year_dir / f'{taken_time.month:02d}'
    else:
        logger.warning(f'⚠️ Could not detect capture date for "{file_path}". Placing in "unknown_date".')
        month_dir = output_dir / 'unknown_date'
    month_dir.mkdir(parents=True, exist_ok=True)
    target_file_path = month_dir / file_path.name

    unique_id = None

    if target_file_path.exists():
        try:
            is_duplicate = are_files_identical(file_1=file_path, file_2=target_file_path)
        except OSError as e:
            raise ProcessFileError(
                f'While processing a file {file_path} target file {target_file_path} already exists. '
                f'Error while trying to detect if files are duplicates: {e}. '
                f'You should check this file manually in the source directory.'
            ) from e

        if is_duplicate:
            logger.warning(f'📄 Skip copying duplicate:\n  from: "{file_path}"\n  to: "{target_file_path}"')
            metadata_result = copy_supplemental_metadata_json(
                file_path=file_path,
                target_dir=month_dir,
                unique_id=None,
                use_hardlinks=use_hardlinks,
            )
            return {
                'media_status': 'duplicate',
                'metadata_path': metadata_result['metadata_path'],
                'metadata_status': metadata_result['status'],
            }
        else:
            unique_id = uuid.uuid4().hex
            unique_name = f'{file_path.stem}_{unique_id}{file_path.suffix}'
            old_target_file_path = target_file_path
            target_file_path = month_dir / unique_name
            logger.warning(
                f'🔄 File "{old_target_file_path}" exists but it is not a duplicate. Renaming to "{unique_name}".'
            )

    try:
        copy_file_or_create_hardlink(
            src=file_path, dst=target_file_path, use_hardlinks=use_hardlinks, is_metadata_file=False
        )
    except CreateHardlinkOrCopyFileError as e:
        raise ProcessFileError(f'{e}') from e

    # update file timestamps to preserve original capture date
    if taken_time:
        set_file_timestamps(target_file_path, taken_time)

    # copy the supplemental metadata JSON file if it exists
    metadata_result = copy_supplemental_metadata_json(
        file_path=file_path,
        target_dir=month_dir,
        unique_id=unique_id,
        use_hardlinks=use_hardlinks,
    )

    return {
        'media_status': 'copied',
        'metadata_path': metadata_result['metadata_path'],
        'metadata_status': metadata_result['status'],
    }


def process_files(input_dir: Path, output_dir: Path, valid_extensions: set, use_hardlinks: bool) -> dict:
    """
    Process all files in the input directory.

    Each file is categorized into exactly one of:
    - copied: successfully placed in output (media files and their metadata)
    - duplicates: skipped as identical to a file already in output
    - not_copied: not placed in output, needs replication (non-media files, metadata conflicts, orphan metadata).

    :param input_dir: Path to the directory containing files to process.
    :param output_dir: Directory where processed files will be stored, organized by date.
    :param valid_extensions: Set of valid file extensions to include in processing.
    :param use_hardlinks: If True, creates hardlinks instead of copying files.
    :return: A dict with 'copied', 'duplicates', and 'not_copied' lists of Path.
    :raises ProcessFileError:
    """
    copied = []
    duplicates = []
    not_copied = []

    metadata_expected: set[Path] = set()
    metadata_handled: set[Path] = set()

    for file_path in input_dir.rglob('*'):
        if file_path.is_dir():
            continue

        if IGNORED_DIRS & set(file_path.parts):
            logger.debug(f'Ignoring {file_path}')
            continue

        if file_path.suffix.lower() not in valid_extensions:
            if _is_supplemental_metadata_json(file_path):
                logger.debug(f'Metadata file (will be handled with its media file): {file_path}')
                metadata_expected.add(file_path)
            else:
                logger.debug(f'Not a media file: {file_path}')
                not_copied.append(file_path)
            continue

        # media file
        result = proceed_file(file_path, output_dir, use_hardlinks)

        # categorize media file
        if result['media_status'] == 'copied':
            copied.append(file_path)
        else:
            duplicates.append(file_path)

        # categorize metadata file (skip if already handled by a previous media file —
        # truncation collisions can cause multiple media to find the same metadata)
        metadata_path = result['metadata_path']
        if metadata_path and metadata_path not in metadata_handled:
            metadata_handled.add(metadata_path)
            status = result['metadata_status']
            if status == 'copied':
                copied.append(metadata_path)
            elif status == 'duplicate':
                duplicates.append(metadata_path)
            else:  # "conflict" or "error"
                not_copied.append(metadata_path)

    # metadata files seen in main loop but not handled by any proceed_file call
    orphan_metadata = metadata_expected - metadata_handled
    for m in sorted(orphan_metadata):
        logger.debug(f'Orphan metadata (not associated with any media file): {m}')
        not_copied.append(m)

    return {
        'copied': copied,
        'duplicates': duplicates,
        'not_copied': not_copied,
    }


def main() -> int:
    """Run the CLI application to sort photos and videos by date."""
    start_time = time.perf_counter()

    parser = argparse.ArgumentParser(description='Sort photos by date.')
    parser.add_argument('--input-dir', required=True, type=Path, help='Directory with input files')
    parser.add_argument('--output-dir', required=True, type=Path, help='Directory to store sorted files')
    parser.add_argument(
        '--use-hardlinks',
        action='store_true',
        help='Use hardlinks for files in the output directory (default: copies files)',
    )
    parser.add_argument('--verbose', action='store_true', help='Enable debug logging')
    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir
    use_hardlinks = args.use_hardlinks
    verbose = args.verbose

    # configure root logger, all project loggers will inherit this configuration
    configure_root_logger(verbose)
    # set WARNING level for third-party libs
    configure_third_party_loggers()

    # 1. count files in input dir
    input_dir_stat = count_files(input_dir, VALID_PHOTO_EXTENSIONS, VALID_VIDEO_EXTENSIONS)

    # 2. process files
    logger.info(LOG_SEPARATOR)
    logger.info('Processing files...')
    try:
        result = process_files(
            input_dir=input_dir,
            output_dir=output_dir,
            valid_extensions=VALID_EXTENSIONS,
            use_hardlinks=use_hardlinks,
        )
    except ProcessFileError as e:
        logger.error(f'🛑 {e}')
        return 1

    copied = result['copied']
    duplicates = result['duplicates']
    not_copied = result['not_copied']

    logger.info(f'Files copied: {len(copied)}')
    logger.info(f'Duplicates skipped: {len(duplicates)}')
    logger.info(f'Files to replicate: {len(not_copied)}')
    logger.info('✅ Sorting completed successfully!')
    logger.info(LOG_SEPARATOR + '\n')

    # 3. replicate not_copied files
    logger.info(LOG_SEPARATOR)
    run_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    hardlink_dir = output_dir / f'missed_files_{run_timestamp}'
    replicate_files_with_structure(
        files=not_copied,
        input_dir=input_dir,
        hardlink_dir=hardlink_dir,
        use_hardlinks=use_hardlinks,
    )
    logger.info(LOG_SEPARATOR + '\n')

    # 4. count files in output dir (after not_copied files were added)
    count_files(output_dir, VALID_PHOTO_EXTENSIONS, VALID_VIDEO_EXTENSIONS)

    # 5. integrity check: every input file is accounted for in exactly one category
    logger.info(LOG_SEPARATOR)
    total_accounted = len(copied) + len(duplicates) + len(not_copied)
    msg = (
        f'{input_dir_stat["total_files"]} (input) == '
        f'{len(copied)} (copied) + '
        f'{len(duplicates)} (duplicates) + '
        f'{len(not_copied)} (not copied)'
    )
    if input_dir_stat['total_files'] != total_accounted:
        logger.error('🛑 ' + msg.replace('==', '!='))
        return 1
    else:
        logger.info('✅ ' + msg)
    logger.info(LOG_SEPARATOR + '\n')

    execution_time = time.perf_counter() - start_time
    logger.debug(f'⏱️  Execution time: {execution_time:.2f} seconds')
    return 0


if __name__ == '__main__':
    sys.exit(main())
