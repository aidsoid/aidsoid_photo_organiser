# Copyright (c) 2026 Alexey Doroshenko <aidsoid@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later OR Commercial
# See LICENSE and COMMERCIAL_LICENSE.md for details.

"""Unit tests for get_date_from_json."""

from datetime import UTC, datetime
from pathlib import Path

from aidsoid_photo_organiser.detect_taken_time.get_date_from_json import get_date_from_json


class TestGetDateFromJson:
    """Grouped tests for `get_date_from_json`."""

    def test__get_date_from_json__valid_json__success(self, tmp_path: Path):
        """JSON with photoTakenTime.timestamp returns correct UTC datetime."""
        # given:
        media_file = tmp_path / 'photo.jpg'
        media_file.touch()

        metadata_file = tmp_path / 'photo.jpg.supplemental-metadata.json'
        metadata_file.write_text('{"photoTakenTime": {"timestamp": "1563180645"}}')

        expected = datetime(2019, 7, 15, 8, 50, 45, tzinfo=UTC)

        # when:
        result = get_date_from_json(file_path=media_file)

        # then:
        assert result == expected

    def test__get_date_from_json__valid_json_long_filename_truncated__success(self, tmp_path: Path):
        """Long filename is truncated to 46 chars before .json per Google Takeout convention."""
        # given:
        media_file = tmp_path / '00100dPORTRAIT_00100_BURST20190825170724237_COV.jpg'
        media_file.touch()

        # "00100dPORTRAIT_00100_BURST20190825170724237_COV.jpg.supplemental-metadata"
        # truncated to 46 chars: "00100dPORTRAIT_00100_BURST20190825170724237_CO"
        metadata_file = tmp_path / '00100dPORTRAIT_00100_BURST20190825170724237_CO.json'
        metadata_file.write_text('{"photoTakenTime": {"timestamp": "1566752844"}}')

        expected = datetime(2019, 8, 25, 17, 7, 24, tzinfo=UTC)

        # when:
        result = get_date_from_json(file_path=media_file)

        # then:
        assert result == expected

    def test__get_date_from_json__without_supplemental_metadata_json__returns_none(self, tmp_path: Path):
        """Media file without accompanying supplemental-metadata.json returns None."""
        # given:
        media_file = tmp_path / 'photo.jpg'
        media_file.touch()

        # when:
        result = get_date_from_json(file_path=media_file)

        # then:
        assert result is None

    def test__get_date_from_json__invalid_json__returns_none(self, tmp_path: Path):
        """Malformed JSON file returns None."""
        # given:
        media_file = tmp_path / 'photo.jpg'
        media_file.touch()

        metadata_file = tmp_path / 'photo.jpg.supplemental-metadata.json'
        metadata_file.write_text('invalid_json')

        # when:
        result = get_date_from_json(file_path=media_file)

        # then:
        assert result is None

    def test__get_date_from_json__without_photo_taken_time_key__returns_none(self, tmp_path: Path):
        """JSON without photoTakenTime key returns None."""
        # given:
        media_file = tmp_path / 'photo.jpg'
        media_file.touch()

        metadata_file = tmp_path / 'photo.jpg.supplemental-metadata.json'
        metadata_file.write_text('{"title": "photo.jpg"}')

        # when:
        result = get_date_from_json(file_path=media_file)

        # then:
        assert result is None

    def test__get_date_from_json__without_timestamp_key__returns_none(self, tmp_path: Path):
        """JSON with photoTakenTime but without timestamp key returns None."""
        # given:
        media_file = tmp_path / 'photo.jpg'
        media_file.touch()

        metadata_file = tmp_path / 'photo.jpg.supplemental-metadata.json'
        metadata_file.write_text('{"photoTakenTime": {}}')

        # when:
        result = get_date_from_json(file_path=media_file)

        # then:
        assert result is None
