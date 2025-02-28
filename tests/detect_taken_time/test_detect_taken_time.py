# Copyright (c) 2026 Alexey Doroshenko <aidsoid@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later OR Commercial
# See LICENSE and COMMERCIAL_LICENSE.md for details.

"""Unit tests for the detect_taken_time orchestrator."""

from datetime import datetime
from pathlib import Path

from aidsoid_photo_organiser.detect_taken_time import detect_taken_time
from aidsoid_photo_organiser.detect_taken_time.get_date_from_ffprobe import ffprobe_time_str_to_datetime


class TestDetectTakenTime:
    """Grouped tests for `detect_taken_time` across various file types and scenarios."""

    def test__detect_taken_time__mp4_with_metadata__success(self):
        """Detect time for MP4 with embedded metadata."""
        # given:
        file_path = Path('tests/files/mp4_with_creation_time.mp4')
        desired_capture_datetime = ffprobe_time_str_to_datetime('2018-11-22T15:26:09.000000Z')

        # when:
        capture_datetime = detect_taken_time(file_path=file_path)

        # then:
        assert capture_datetime == desired_capture_datetime

    def test__detect_taken_time__m4v_with_metadata__success(self):
        """Detect time for M4V with embedded metadata."""
        # given:
        file_path = Path('tests/files/m4v_with_creation_time.m4v')
        desired_capture_datetime = ffprobe_time_str_to_datetime('2018-11-22T15:26:09.000000Z')

        # when:
        capture_datetime = detect_taken_time(file_path=file_path)

        # then:
        assert capture_datetime == desired_capture_datetime

    def test__detect_taken_time__mov_with_metadata__success(self):
        """Detect time for MOV with embedded metadata."""
        # given:
        file_path = Path('tests/files/mov_with_creation_time.mov')
        desired_capture_datetime = ffprobe_time_str_to_datetime('2018-11-22T15:26:09.000000Z')

        # when:
        capture_datetime = detect_taken_time(file_path=file_path)

        # then:
        assert capture_datetime == desired_capture_datetime

    def test__detect_taken_time__mkv_with_metadata__success(self):
        """Detect time for MKV with embedded metadata."""
        # given:
        file_path = Path('tests/files/mkv_with_creation_time.mkv')
        desired_capture_datetime = ffprobe_time_str_to_datetime('2018-11-22T15:26:09.000000Z')

        # when:
        capture_datetime = detect_taken_time(file_path=file_path)

        # then:
        assert capture_datetime == desired_capture_datetime

    def test__detect_taken_time__without_json_without_metadata_with_android_naming___success(self):
        """Extract time from Android VID_ filename when no metadata present."""
        # given:
        file_path = Path('tests/files/VID_20131229_223028.mkv')
        desired_capture_datetime = datetime(year=2013, month=12, day=29, hour=22, minute=30, second=28)

        # when:
        capture_datetime = detect_taken_time(file_path=file_path)

        # then:
        assert capture_datetime == desired_capture_datetime

    def test__detect_taken_time__without_json_without_metadata_without_android_naming___returns_none(self):
        """Returns None when no metadata, naming pattern, or JSON is available."""
        # given:
        file_path = Path('tests/files/mkv_without_creation_time.mkv')

        # when:
        capture_datetime = detect_taken_time(file_path=file_path)

        # then:
        assert capture_datetime is None

    def test__detect_taken_time__png_with_exif__success(self):
        """detect_taken_time extracts date from PNG with EXIF metadata."""
        # given:
        file_path = Path('tests/files/png_with_exif.png')
        expected = datetime(year=2019, month=7, day=15, hour=10, minute=30, second=45)

        # when:
        result = detect_taken_time(file_path=file_path)

        # then:
        assert result == expected

    def test__detect_taken_time__png_without_exif_with_date_in_name__falls_back_to_filename(self):
        """detect_taken_time falls back to filename extraction for PNG without EXIF."""
        # given:
        file_path = Path('tests/files/Screenshot_20210315-142030.png')
        expected = datetime(year=2021, month=3, day=15, hour=14, minute=20, second=30)

        # when:
        result = detect_taken_time(file_path=file_path)

        # then:
        assert result == expected
