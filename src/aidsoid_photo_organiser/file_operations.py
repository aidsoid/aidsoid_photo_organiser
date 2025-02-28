# Copyright (c) 2026 Alexey Doroshenko <aidsoid@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later OR Commercial
# See LICENSE and COMMERCIAL_LICENSE.md for details.

"""File operations: copy, hardlink, hashing and directory comparison utilities."""

import hashlib
import logging
import os
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

logger = logging.getLogger(__name__)


class CreateHardlinkOrCopyFileError(Exception):
    """Base exception for errors occurring during file hardlinking or copying operations."""

    pass


class CreateHardlinkError(CreateHardlinkOrCopyFileError):
    """
    Exception raised when creating a hardlink fails.

    This exception handles errors related to file not found, permission issues,
    and general OS errors when attempting to create a hardlink between two files.
    """

    pass


class CopyFileError(CreateHardlinkOrCopyFileError):
    """
    Exception raised when copying a file fails.

    This exception is triggered by errors such as file not found,
    permission issues, and other OS-related errors during file copying.
    """

    pass


def create_hardlink(src: Path, dst: Path) -> None:
    """
    Create a hardlink from the source file to the destination path.

    :param src: The source file path.
    :param dst: The destination path where the hardlink should be created.
    :raises CreateHardlinkError: If creating the hardlink fails due to file not found,
                                 permission issues, or other OS errors.
    """
    try:
        os.link(src, dst)
    except FileNotFoundError as e:
        raise CreateHardlinkError(f'File not found: "{src}"') from e
    except PermissionError as e:
        raise CreateHardlinkError(f'Permission denied when accessing: "{src}" or "{dst}"') from e
    except FileExistsError as e:
        raise CreateHardlinkError(f'Destination file already exists: "{dst}"') from e
    except OSError as e:
        raise CreateHardlinkError(f'OS error when processing file "{src}" - {e}') from e


def copy_file(src: Path, dst: Path) -> None:
    """
    Copy a file from the source path to the destination path, preserving metadata.

    This function uses `shutil.copy2` to preserve the following file attributes:
    - Modification time (mtime)
    - Access time (atime)
    - File owner and group
    - File permissions

    :param src: The source file path.
    :param dst: The destination path where the file should be copied.
    :raises CopyFileError: If copying the file fails due to file not found,
                           permission issues, or other OS errors.
    """
    try:
        shutil.copy2(src, dst)
    except FileNotFoundError as e:
        raise CopyFileError(f'File not found: "{src}"') from e
    except PermissionError as e:
        raise CopyFileError(f'Permission denied when accessing: "{src}" or "{dst}"') from e
    except FileExistsError as e:
        raise CopyFileError(f'Destination file already exists: "{dst}"') from e
    except OSError as e:
        raise CopyFileError(f'OS error when processing file "{src}" - {e}') from e


def copy_file_or_create_hardlink(src: Path, dst: Path, use_hardlinks: bool, is_metadata_file: bool) -> None:
    """
    Copy a file or create a hardlink based on the provided parameters.

    - If `use_hardlinks` is True, a hardlink is created using `create_hardlink`.
    - Otherwise, the file is copied using `copy_file`.

    :param src: The source file path.
    :param dst: The destination path where the file should be copied or linked.
    :param use_hardlinks: If True, creates a hardlink instead of copying the file.
    :param is_metadata_file: Indicates if the file being processed is a metadata file.
    :raises CreateHardlinkOrCopyFileError: If an error occurs during file operation.
    """
    if use_hardlinks:
        # create a hard link to the file
        create_hardlink(src, dst)
        if is_metadata_file:
            msg = f'🔗 Hardlink created for metadata file: "{src}" to "{dst}".'
        else:
            msg = f'🔗 Hardlink created: "{src}" to "{dst}".'
    else:
        # copy the file to the target directory
        copy_file(src, dst)
        if is_metadata_file:
            msg = f'📄 Copied metadata file: "{src}" to "{dst}".'
        else:
            msg = f'📄 Copied: "{src}" to "{dst}".'
    logger.debug(msg)


def are_files_identical(file_1: Path, file_2: Path) -> bool:
    """
    Check if two files are identical by comparing their BLAKE2b hashes.

    The function first compares file sizes for a quick rejection. If sizes match,
    it then compares BLAKE2b hashes of both files to determine if they are identical.

    :param file_1: Path to the first file.
    :param file_2: Path to the second file.
    :return: True if files are identical, False otherwise.
    :raises OSError: If an error occurs while accessing the files.
    """
    # Compare file sizes first for quick rejection
    if file_1.stat().st_size != file_2.stat().st_size:
        return False

    # Compare file hashes for final validation
    try:
        hash1 = get_file_hash(file_1)
        hash2 = get_file_hash(file_2)
    except OSError:
        raise

    return hash1 == hash2


def get_file_hash(file_path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    """
    Calculate the BLAKE2b hash of a file.

    Uses BLAKE2b instead of SHA-256 for 2-3x faster performance while maintaining
    cryptographic strength sufficient for file deduplication.

    :param file_path: Path to the file to hash.
    :param chunk_size: Size of chunks to read to avoid high memory usage. Defaults to 8 MB.
    :return: The BLAKE2b hash of the file.
    :raises OSError: If the file cannot be accessed or read.
    """
    hasher = hashlib.blake2b()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(chunk_size), b''):
                hasher.update(chunk)
    except OSError as e:
        raise OSError(f'OS error when calculating hash for file "{file_path}" - {e}') from e
    return hasher.hexdigest()


def _get_files_to_hash(directory: Path) -> list[Path]:
    """Get all regular files in directory, excluding @eaDir."""
    exclude_dirs = {'@eaDir'}
    return [
        file_path
        for file_path in directory.rglob('*')
        if file_path.is_file() and not any(component in exclude_dirs for component in file_path.parts)
    ]


def _hash_files_parallel(paths: list[Path]) -> dict[str, Path]:
    """
    Hash a list of Paths in parallel and return a dict hash->Path.

    Defaults to min(32, cpu_count*4) worker threads.
    If multiple files have the same hash, the last one wins (dict overwrites).
    Exceptions from future.result() propagate to the caller.
    """
    if not paths:
        return {}

    default_max_workers = 32
    workers_per_cpu = 4
    max_workers = min(default_max_workers, (os.cpu_count() or 1) * workers_per_cpu)

    hash_to_path: dict[str, Path] = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_path = {executor.submit(get_file_hash, p): p for p in paths}
        for future in as_completed(future_to_path):
            path = future_to_path[future]
            file_hash = future.result()
            hash_to_path[file_hash] = path

    return hash_to_path


def compare_directories(dir1: Path, dir2: Path) -> list[Path]:
    """
    Compare directories using parallel hashing for speed.

    Returns the list of files present in `dir1` whose content-hash is not
    present in `dir2`.
    """
    source_paths = _get_files_to_hash(dir1)
    target_paths = _get_files_to_hash(dir2)

    source_hashes = _hash_files_parallel(source_paths)
    target_hashes = _hash_files_parallel(target_paths)

    return [file for content_hash, file in source_hashes.items() if content_hash not in target_hashes]
