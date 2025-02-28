# Copyright (c) 2026 Alexey Doroshenko <aidsoid@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later OR Commercial
# See LICENSE and COMMERCIAL_LICENSE.md for details.

"""Unit tests for get_date_from_mp4_atoms."""

from pathlib import Path

from aidsoid_photo_organiser.detect_taken_time.get_date_from_ffprobe import ffprobe_time_str_to_datetime
from aidsoid_photo_organiser.detect_taken_time.get_date_from_mp4_atoms import get_date_from_mp4_atoms


class TestGetDateFromMp4Atoms:
    """Grouped tests for `get_date_from_mp4_atoms`."""

    def test__get_date_from_mp4_atoms__mp4_with_creation_time__success(self):
        """MP4 with creation_time returns expected datetime."""
        # given:
        file_path = Path('tests/files/mp4_with_creation_time.mp4')
        expected = ffprobe_time_str_to_datetime('2018-11-22T15:26:09.000000Z')

        # when:
        result = get_date_from_mp4_atoms(file_path=file_path)

        # then:
        assert result == expected

    def test__get_date_from_mp4_atoms__mp4_without_creation_time__returns_none(self):
        """MP4 without creation_time returns None."""
        # given:
        file_path = Path('tests/files/mp4_without_creation_time.mp4')

        # when:
        result = get_date_from_mp4_atoms(file_path=file_path)

        # then:
        assert result is None

    def test__get_date_from_mp4_atoms__m4v_with_creation_time__success(self):
        """M4V with creation_time returns expected datetime."""
        # given:
        file_path = Path('tests/files/m4v_with_creation_time.m4v')
        expected = ffprobe_time_str_to_datetime('2018-11-22T15:26:09.000000Z')

        # when:
        result = get_date_from_mp4_atoms(file_path=file_path)

        # then:
        assert result == expected

    def test__get_date_from_mp4_atoms__m4v_without_creation_time__returns_none(self):
        """M4V without creation_time returns None."""
        # given:
        file_path = Path('tests/files/m4v_without_creation_time.m4v')

        # when:
        result = get_date_from_mp4_atoms(file_path=file_path)

        # then:
        assert result is None

    def test__get_date_from_mp4_atoms__mov_with_creation_time__success(self):
        """MOV with creation_time returns expected datetime."""
        # given:
        file_path = Path('tests/files/mov_with_creation_time.mov')
        expected = ffprobe_time_str_to_datetime('2018-11-22T15:26:09.000000Z')

        # when:
        result = get_date_from_mp4_atoms(file_path=file_path)

        # then:
        assert result == expected

    def test__get_date_from_mp4_atoms__mov_without_creation_time__returns_none(self):
        """MOV without creation_time returns None."""
        # given:
        file_path = Path('tests/files/mov_without_creation_time.mov')

        # when:
        result = get_date_from_mp4_atoms(file_path=file_path)

        # then:
        assert result is None
