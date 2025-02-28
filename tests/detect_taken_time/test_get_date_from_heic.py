# Copyright (c) 2026 Alexey Doroshenko <aidsoid@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later OR Commercial
# See LICENSE and COMMERCIAL_LICENSE.md for details.

"""Unit tests for get_date_from_heic."""

from datetime import datetime
from pathlib import Path

from aidsoid_photo_organiser.detect_taken_time.get_date_from_heic import get_date_from_heic


class TestGetDateFromHeic:
    """Grouped tests for `get_date_from_heic`."""

    # --- .heic ---

    def test__get_date_from_heic__heic_with_exif__success(self):
        """HEIC with EXIF DateTimeOriginal returns correct datetime."""
        # given:
        file_path = Path('tests/files/heic_with_exif.heic')
        expected = datetime(year=2019, month=7, day=15, hour=10, minute=30, second=45)

        # when:
        result = get_date_from_heic(file_path=file_path)

        # then:
        assert result == expected

    def test__get_date_from_heic__heic_without_exif__returns_none(self):
        """HEIC without EXIF metadata returns None."""
        # given:
        file_path = Path('tests/files/heic_without_exif.heic')

        # when:
        result = get_date_from_heic(file_path=file_path)

        # then:
        assert result is None

    def test__get_date_from_heic__heic_with_exif_no_date__returns_none(self):
        """HEIC with EXIF metadata but without DateTimeOriginal returns None."""
        # given:
        file_path = Path('tests/files/heic_with_exif_no_date.heic')

        # when:
        result = get_date_from_heic(file_path=file_path)

        # then:
        assert result is None

    # --- .heif ---

    def test__get_date_from_heic__heif_with_exif__success(self):
        """HEIF with EXIF DateTimeOriginal returns correct datetime."""
        # given:
        file_path = Path('tests/files/heif_with_exif.heif')
        expected = datetime(year=2019, month=7, day=15, hour=10, minute=30, second=45)

        # when:
        result = get_date_from_heic(file_path=file_path)

        # then:
        assert result == expected

    def test__get_date_from_heic__heif_without_exif__returns_none(self):
        """HEIF without EXIF metadata returns None."""
        # given:
        file_path = Path('tests/files/heif_without_exif.heif')

        # when:
        result = get_date_from_heic(file_path=file_path)

        # then:
        assert result is None

    # --- edge cases ---

    def test__get_date_from_heic__nonexistent_file__returns_none(self):
        """Non-existent file returns None."""
        # given:
        file_path = Path('tests/files/nonexistent.heic')

        # when:
        result = get_date_from_heic(file_path=file_path)

        # then:
        assert result is None

    def test__get_date_from_heic__non_image_file__returns_none(self, tmp_path):
        """Non-image file returns None."""
        # given:
        file_path = tmp_path / 'not_an_image.heic'
        file_path.write_text('this is not an image')

        # when:
        result = get_date_from_heic(file_path=file_path)

        # then:
        assert result is None
