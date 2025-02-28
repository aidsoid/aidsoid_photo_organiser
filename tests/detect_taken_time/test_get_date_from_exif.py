# Copyright (c) 2026 Alexey Doroshenko <aidsoid@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later OR Commercial
# See LICENSE and COMMERCIAL_LICENSE.md for details.

"""Unit tests for get_date_from_exif."""

from datetime import datetime
from pathlib import Path

from aidsoid_photo_organiser.detect_taken_time.get_date_from_exif import get_date_from_exif


class TestGetDateFromExif:
    """Grouped tests for `get_date_from_exif`."""

    def test__get_date_from_exif__jpg_with_exif__success(self):
        """JPEG with EXIF DateTimeOriginal returns correct datetime."""
        # given:
        file_path = Path('tests/files/jpg_with_exif.jpg')
        expected = datetime(year=2019, month=7, day=15, hour=10, minute=30, second=45)

        # when:
        result = get_date_from_exif(file_path=file_path)

        # then:
        assert result == expected

    def test__get_date_from_exif__jpg_without_exif__returns_none(self):
        """JPEG without EXIF metadata returns None."""
        # given:
        file_path = Path('tests/files/jpg_without_exif.jpg')

        # when:
        result = get_date_from_exif(file_path=file_path)

        # then:
        assert result is None

    def test__get_date_from_exif__jpg_with_exif_no_date__returns_none(self):
        """JPEG with EXIF metadata but without DateTimeOriginal returns None."""
        # given:
        file_path = Path('tests/files/jpg_with_exif_no_date.jpg')

        # when:
        result = get_date_from_exif(file_path=file_path)

        # then:
        assert result is None

    def test__get_date_from_exif__nonexistent_file__returns_none(self):
        """Non-existent file returns None."""
        # given:
        file_path = Path('tests/files/nonexistent.jpg')

        # when:
        result = get_date_from_exif(file_path=file_path)

        # then:
        assert result is None

    def test__get_date_from_exif__non_image_file__returns_none(self, tmp_path):
        """Non-image file returns None."""
        # given:
        file_path = tmp_path / 'not_an_image.txt'
        file_path.write_text('this is not an image')

        # when:
        result = get_date_from_exif(file_path=file_path)

        # then:
        assert result is None
