# Copyright (c) 2026 Alexey Doroshenko <aidsoid@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later OR Commercial
# See LICENSE and COMMERCIAL_LICENSE.md for details.

"""Unit tests for get_date_from_ffprobe."""

from pathlib import Path
from unittest.mock import patch

import ffmpeg
import pytest

from aidsoid_photo_organiser.detect_taken_time.get_date_from_ffprobe import (
    _is_ffprobe_available,
    ffprobe_time_str_to_datetime,
    get_date_from_ffprobe,
)


@pytest.fixture()
def _clear_ffprobe_cache():
    """Clear the lru_cache before and after the test."""
    _is_ffprobe_available.cache_clear()
    yield
    _is_ffprobe_available.cache_clear()


class TestGetDateFromFfprobe:
    """Grouped tests for `get_date_from_ffprobe`."""

    # --- MP4 ---

    def test__get_date_from_ffprobe__mp4_with_creation_time__success(self):
        """MP4 with creation_time returns datetime."""
        # given:
        file_path = Path('tests/files/mp4_with_creation_time.mp4')
        expected = ffprobe_time_str_to_datetime('2018-11-22T15:26:09.000000Z')

        # when:
        result = get_date_from_ffprobe(file_path=file_path)

        # then:
        assert result == expected

    def test__get_date_from_ffprobe__mp4_without_creation_time__returns_none(self):
        """MP4 without creation_time returns None."""
        # given:
        file_path = Path('tests/files/mp4_without_creation_time.mp4')

        # when:
        result = get_date_from_ffprobe(file_path=file_path)

        # then:
        assert result is None

    # --- M4V ---

    def test__get_date_from_ffprobe__m4v_with_creation_time__success(self):
        """M4V with creation_time returns datetime."""
        # given:
        file_path = Path('tests/files/m4v_with_creation_time.m4v')
        expected = ffprobe_time_str_to_datetime('2018-11-22T15:26:09.000000Z')

        # when:
        result = get_date_from_ffprobe(file_path=file_path)

        # then:
        assert result == expected

    def test__get_date_from_ffprobe__m4v_without_creation_time__returns_none(self):
        """M4V without creation_time returns None."""
        # given:
        file_path = Path('tests/files/m4v_without_creation_time.m4v')

        # when:
        result = get_date_from_ffprobe(file_path=file_path)

        # then:
        assert result is None

    # --- MOV ---

    def test__get_date_from_ffprobe__mov_with_creation_time__success(self):
        """MOV with creation_time returns datetime."""
        # given:
        file_path = Path('tests/files/mov_with_creation_time.mov')
        expected = ffprobe_time_str_to_datetime('2018-11-22T15:26:09.000000Z')

        # when:
        result = get_date_from_ffprobe(file_path=file_path)

        # then:
        assert result == expected

    def test__get_date_from_ffprobe__mov_without_creation_time__returns_none(self):
        """MOV without creation_time returns None."""
        # given:
        file_path = Path('tests/files/mov_without_creation_time.mov')

        # when:
        result = get_date_from_ffprobe(file_path=file_path)

        # then:
        assert result is None

    # --- MKV ---

    def test__get_date_from_ffprobe__mkv_with_creation_time__success(self):
        """MKV with creation_time returns datetime."""
        # given:
        file_path = Path('tests/files/mkv_with_creation_time.mkv')
        expected = ffprobe_time_str_to_datetime('2018-11-22T15:26:09.000000Z')

        # when:
        result = get_date_from_ffprobe(file_path=file_path)

        # then:
        assert result == expected

    def test__get_date_from_ffprobe__mkv_without_creation_time__returns_none(self):
        """MKV without creation_time returns None."""
        # given:
        file_path = Path('tests/files/mkv_without_creation_time.mkv')

        # when:
        result = get_date_from_ffprobe(file_path=file_path)

        # then:
        assert result is None

    # --- ffprobe not installed ---

    @pytest.mark.usefixtures('_clear_ffprobe_cache')
    @patch('aidsoid_photo_organiser.detect_taken_time.get_date_from_ffprobe.shutil.which', return_value=None)
    def test__get_date_from_ffprobe__ffprobe_not_installed__returns_none(self, _mock_which, caplog):
        """When ffprobe is not installed, returns None and logs a warning."""
        # given:
        file_path = Path('tests/files/mp4_with_creation_time.mp4')

        # when:
        with caplog.at_level('WARNING'):
            result = get_date_from_ffprobe(file_path=file_path)

        # then:
        assert result is None
        assert 'ffprobe not found in PATH' in caplog.text

    # --- ffprobe removed after running ---

    @patch(
        'aidsoid_photo_organiser.detect_taken_time.get_date_from_ffprobe.ffmpeg.probe',
        side_effect=FileNotFoundError,
    )
    def test__get_date_from_ffprobe__ffprobe_removed_after_running__returns_none(self, _mock_probe, caplog):
        """When ffprobe is removed while the script is running, returns None and logs a warning."""
        # given:
        file_path = Path('tests/files/mp4_with_creation_time.mp4')

        # when:
        with caplog.at_level('WARNING'):
            result = get_date_from_ffprobe(file_path=file_path)

        # then:
        assert result is None
        assert 'ffprobe not found' in caplog.text

    # --- invalid file ---

    @patch(
        'aidsoid_photo_organiser.detect_taken_time.get_date_from_ffprobe.ffmpeg.probe',
        side_effect=ffmpeg.Error('ffprobe', stdout=b'', stderr=b'Invalid data found'),
    )
    def test__get_date_from_ffprobe__invalid_file__returns_none(self, _mock_probe, caplog):
        """When ffprobe fails to read the file, returns None and logs a warning."""
        # given:
        file_path = Path('tests/files/mp4_with_creation_time.mp4')

        # when:
        with caplog.at_level('WARNING'):
            result = get_date_from_ffprobe(file_path=file_path)

        # then:
        assert result is None
        assert 'Unable to retrieve video metadata' in caplog.text

    # --- unexpected error ---

    @patch(
        'aidsoid_photo_organiser.detect_taken_time.get_date_from_ffprobe.ffmpeg.probe',
        side_effect=RuntimeError('something went wrong'),
    )
    def test__get_date_from_ffprobe__unexpected_error__returns_none(self, _mock_probe, caplog):
        """When an unexpected exception occurs, returns None and logs a warning."""
        # given:
        file_path = Path('tests/files/mp4_with_creation_time.mp4')

        # when:
        with caplog.at_level('WARNING'):
            result = get_date_from_ffprobe(file_path=file_path)

        # then:
        assert result is None
        assert 'unexpected error occurred' in caplog.text
