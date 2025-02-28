# Copyright (c) 2026 Alexey Doroshenko <aidsoid@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later OR Commercial
# See LICENSE and COMMERCIAL_LICENSE.md for details.

"""Unit tests for get_date_from_png."""

from datetime import datetime
from pathlib import Path

from aidsoid_photo_organiser.detect_taken_time.get_date_from_png import get_date_from_png


class TestGetDateFromPng:
    """Grouped tests for `get_date_from_png`."""

    def test__get_date_from_png__png_with_exif__success(self):
        """PNG with eXIf chunk containing DateTimeOriginal returns correct datetime."""
        # given:
        file_path = Path('tests/files/png_with_exif.png')
        expected = datetime(year=2019, month=7, day=15, hour=10, minute=30, second=45)

        # when:
        result = get_date_from_png(file_path=file_path)

        # then:
        assert result == expected

    def test__get_date_from_png__png_without_exif__returns_none(self):
        """PNG without EXIF metadata returns None."""
        # given:
        file_path = Path('tests/files/png_without_exif.png')

        # when:
        result = get_date_from_png(file_path=file_path)

        # then:
        assert result is None

    def test__get_date_from_png__png_with_exif_no_date__returns_none(self):
        """PNG with EXIF metadata but without DateTimeOriginal returns None."""
        # given:
        file_path = Path('tests/files/png_with_exif_no_date.png')

        # when:
        result = get_date_from_png(file_path=file_path)

        # then:
        assert result is None
