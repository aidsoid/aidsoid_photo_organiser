# Copyright (c) 2026 Alexey Doroshenko <aidsoid@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later OR Commercial
# See LICENSE and COMMERCIAL_LICENSE.md for details.

"""Performance test for directory comparison."""

import os
import shutil
import time
from pathlib import Path

import pytest

import aidsoid_photo_organiser.file_operations as file_operations


def _create_files(directory: Path, count: int, size_bytes: int):
    directory.mkdir(parents=True, exist_ok=True)
    for i in range(count):
        p = directory / f'file_{i:06d}.bin'
        with open(p, 'wb') as f:
            f.write(os.urandom(size_bytes))


def _run_and_time(func, src: Path, dst: Path):
    start = time.perf_counter()
    missing = func(src, dst)
    elapsed = time.perf_counter() - start
    print(f'{func.__name__}: elapsed={elapsed:.3f}s missing={len(missing)}')
    return elapsed, missing


@pytest.mark.slow
def test_compare_directories_10000(tmp_path):
    """
    Measure `compare_directories` on 10k files.

    This test only asserts completion and prints elapsed time.
    """
    count = 10000
    size = 64 * 1024

    src = tmp_path / 'src'
    dst = tmp_path / 'dst'

    _create_files(src, count, size)
    shutil.copytree(src, dst)

    elapsed, missing = _run_and_time(file_operations.compare_directories, src, dst)
    assert len(missing) == 0
