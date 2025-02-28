# Copyright (c) 2026 Alexey Doroshenko <aidsoid@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later OR Commercial
# See LICENSE and COMMERCIAL_LICENSE.md for details.

"""Shared constants."""

IGNORED_DIRS = {'@eaDir'}

VALID_PHOTO_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.heic', '.heif', '.cr2', '.gif'}
VALID_VIDEO_EXTENSIONS = {'.mp4', '.m4v', '.mov', '.avi', '.hevc', '.mkv', '.mp'}
VALID_EXTENSIONS = VALID_PHOTO_EXTENSIONS | VALID_VIDEO_EXTENSIONS

LOG_SEPARATOR = '=' * 50
