# Copyright (c) 2026 Alexey Doroshenko <aidsoid@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later OR Commercial
# See LICENSE and COMMERCIAL_LICENSE.md for details.

"""Utilities for setting file timestamps."""

import os
import sys
from datetime import datetime
from pathlib import Path


def set_file_timestamps(file_path: Path, timestamp: datetime) -> None:
    """
    Set the file's access and modification times to the given timestamp.

    On macOS, setting mtime earlier than birth time also updates birth time.
    On Windows, the creation time is explicitly set via the Win32 API.
    On Linux, only atime and mtime can be updated (birth time is not settable).
    """
    epoch_time = timestamp.timestamp()
    os.utime(file_path, (epoch_time, epoch_time))

    if sys.platform == 'win32':
        _set_creation_time_win32(file_path, epoch_time)


def _set_creation_time_win32(file_path: Path, epoch_time: float) -> None:
    """Set the file creation time on Windows using the Win32 API."""
    import ctypes
    from ctypes import wintypes

    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)  # type: ignore[attr-defined]

    GENERIC_WRITE = 0x40000000  # noqa: N806
    OPEN_EXISTING = 3  # noqa: N806
    FILE_ATTRIBUTE_NORMAL = 0x80  # noqa: N806

    # Convert Unix epoch to Windows FILETIME (100-ns intervals since 1601-01-01)
    EPOCH_AS_FILETIME = 116444736000000000  # noqa: N806
    filetime_int = int(epoch_time * 10_000_000) + EPOCH_AS_FILETIME
    creation_time = wintypes.FILETIME(filetime_int & 0xFFFFFFFF, filetime_int >> 32)

    handle = kernel32.CreateFileW(str(file_path), GENERIC_WRITE, 0, None, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, None)
    if handle == wintypes.HANDLE(-1).value:
        return

    try:
        kernel32.SetFileTime(handle, ctypes.byref(creation_time), None, None)
    finally:
        kernel32.CloseHandle(handle)
