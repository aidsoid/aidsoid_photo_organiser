# Copyright (c) 2026 Alexey Doroshenko <aidsoid@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later OR Commercial
# See LICENSE and COMMERCIAL_LICENSE.md for details.

"""Aidsoid Photo Organiser - A tool for organizing photos and videos based on capture time."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version('aidsoid-photo-organiser')
except PackageNotFoundError:
    __version__ = '0.0.0'
