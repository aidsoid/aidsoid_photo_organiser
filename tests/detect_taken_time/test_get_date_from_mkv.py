# Copyright (c) 2026 Alexey Doroshenko <aidsoid@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later OR Commercial
# See LICENSE and COMMERCIAL_LICENSE.md for details.

"""Unit tests for get_date_from_mkv."""

from pathlib import Path

from aidsoid_photo_organiser.detect_taken_time.get_date_from_ffprobe import ffprobe_time_str_to_datetime
from aidsoid_photo_organiser.detect_taken_time.get_date_from_mkv import get_date_from_mkv


class TestGetDateFromMkv:
    """Grouped tests for `get_date_from_mkv`."""

    def test__get_date_from_mkv__mkv_with_creation_time__success(self):
        """Direct test for get_date_from_mkv using the MKV file that has a DateUTC."""
        # given:
        file_path = Path('tests/files/mkv_with_creation_time.mkv')
        expected = ffprobe_time_str_to_datetime('2018-11-22T15:26:09.000000Z')

        # when:
        result = get_date_from_mkv(file_path=file_path)

        # then:
        assert result == expected

    def test__get_date_from_mkv__mkv_without_creation_time__returns_none(self):
        """MKV without creation_time returns None."""
        # given:
        file_path = Path('tests/files/mkv_without_creation_time.mkv')

        # when:
        result = get_date_from_mkv(file_path=file_path)

        # then:
        assert result is None
