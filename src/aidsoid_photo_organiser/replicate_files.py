# Copyright (c) 2026 Alexey Doroshenko <aidsoid@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later OR Commercial
# See LICENSE and COMMERCIAL_LICENSE.md for details.

"""Replicate files preserving directory structure by copying or hardlinking."""

import logging
from pathlib import Path

from .file_operations import CreateHardlinkOrCopyFileError, copy_file_or_create_hardlink

logger = logging.getLogger(__name__)


def replicate_files_with_structure(
    files: list[Path],
    input_dir: Path,
    hardlink_dir: Path,
    use_hardlinks: bool = False,
) -> None:
    """
    Create hardlinks or copies for the given files in the specified directory.

    Preserve the directory structure relative to ``input_dir``.

    :param files: List of file paths to create hardlinks or copies for.
    :param input_dir: The original input directory to preserve relative paths.
    :param hardlink_dir: The directory where hardlinks or copies will be created.
    :param use_hardlinks: If True, creates hardlinks; otherwise, copies files.

    """
    if not files:
        logger.info('✅ No files to process.')
        return

    operation = 'hardlinks' if use_hardlinks else 'copies'
    logger.info(f'📁 Creating {operation} for {len(files)} files...')

    for source_path in files:
        # Calculate the relative path of the file to the input directory
        relative_path = source_path.relative_to(input_dir)

        # Determine the target path in the output directory
        target_path = hardlink_dir / relative_path

        # Create necessary directories
        target_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            copy_file_or_create_hardlink(
                src=source_path, dst=target_path, use_hardlinks=use_hardlinks, is_metadata_file=False
            )
        except CreateHardlinkOrCopyFileError as e:
            logger.warning(f'🛑 Error processing "{source_path}": {e}')

    logger.info(f'✅ {operation.capitalize()} creation completed.')
