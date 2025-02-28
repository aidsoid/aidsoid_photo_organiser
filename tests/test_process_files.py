# Copyright (c) 2026 Alexey Doroshenko <aidsoid@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later OR Commercial
# See LICENSE and COMMERCIAL_LICENSE.md for details.

"""Unit tests for process_files."""

import json
from datetime import datetime
from pathlib import Path

from aidsoid_photo_organiser.constants import IGNORED_DIRS, VALID_EXTENSIONS
from aidsoid_photo_organiser.main import process_files


def _create_media_file(path: Path, content: bytes = b'\xff\xd8\xff\xe0' + b'\x00' * 100) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


def _create_metadata_json(media_path: Path, timestamp: str) -> Path:
    """
    Create a supplemental metadata JSON for the given media file.

    Follows Google Takeout naming: <filename>.supplemental-metadata.json
    truncated to 46 chars + .json
    """
    with_suffix = f'{media_path.name}.supplemental-metadata'
    truncated = with_suffix[:46]
    metadata_filename = f'{truncated}.json'
    metadata_path = media_path.parent / metadata_filename
    metadata_path.parent.mkdir(parents=True, exist_ok=True)

    metadata_content = {
        'title': media_path.name,
        'photoTakenTime': {'timestamp': timestamp},
    }
    metadata_path.write_text(json.dumps(metadata_content))
    return metadata_path


class TestProcessFiles:
    """Tests for the `process_files` function and related behaviors."""

    def test__single_media__copied(self, tmp_path, monkeypatch):
        """Single media file without metadata is copied."""
        # given:
        input_dir = tmp_path / 'input'
        output_dir = tmp_path / 'output'
        _create_media_file(input_dir / 'photo.jpg')
        output_dir.mkdir()
        monkeypatch.setattr('aidsoid_photo_organiser.main.detect_taken_time', lambda _: datetime(2019, 1, 1))

        # when:
        result = process_files(
            input_dir=input_dir,
            output_dir=output_dir,
            valid_extensions=VALID_EXTENSIONS,
            use_hardlinks=False,
        )

        # then:
        # and: media is copied, no duplicates or not_copied
        assert len(result['copied']) == 1
        assert len(result['duplicates']) == 0
        assert len(result['not_copied']) == 0

        # and: media is in correct location
        assert (output_dir / '2019' / '01' / 'photo.jpg').exists()

    def test__media_with_metadata__both_copied(self, tmp_path):
        """Media file with supplemental metadata JSON — both are copied."""
        # given:
        input_dir = tmp_path / 'input'
        output_dir = tmp_path / 'output'
        media = _create_media_file(input_dir / 'photo.jpg')
        _create_metadata_json(media, timestamp='1546300800')  # 2019-01-01 00:00:00 UTC
        output_dir.mkdir()

        # when:
        result = process_files(
            input_dir=input_dir,
            output_dir=output_dir,
            valid_extensions=VALID_EXTENSIONS,
            use_hardlinks=False,
        )

        # then:
        # and: both media and metadata are copied
        assert len(result['copied']) == 2
        assert len(result['duplicates']) == 0
        assert len(result['not_copied']) == 0

        # and: media is in correct location
        assert (output_dir / '2019' / '01' / 'photo.jpg').exists()

        # and: metadata is in same location
        assert (output_dir / '2019' / '01' / 'photo.jpg.supplemental-metadata.json').exists()

    def test__media_with_metadata_and_orphan_metadata__orphan_not_copied(self, tmp_path):
        """Orphan metadata (no matching media) goes to not_copied."""
        # given:
        input_dir = tmp_path / 'input'
        output_dir = tmp_path / 'output'
        media = _create_media_file(input_dir / 'photo.jpg')
        _create_metadata_json(media, timestamp='1546300800')  # 2019-01-01 00:00:00 UTC
        _create_metadata_json(input_dir / 'deleted_photo.jpg', timestamp='1546300800')
        output_dir.mkdir()

        # when:
        result = process_files(
            input_dir=input_dir,
            output_dir=output_dir,
            valid_extensions=VALID_EXTENSIONS,
            use_hardlinks=False,
        )

        # then:
        # and: media and its metadata are copied, but orphan metadata is not
        assert len(result['copied']) == 2
        assert len(result['duplicates']) == 0
        assert len(result['not_copied']) == 1

        # and: orphan metadata filename contains "deleted_photo"
        orphan_path = result['not_copied'][0]
        assert 'deleted_photo' in orphan_path.name

        # and: orphan metadata is not in output
        assert not list(output_dir.rglob('*deleted_photo*'))

    def test__two_different_media_in_subdirs__both_copied(self, tmp_path, monkeypatch):
        """Two non-duplicate media files in different subdirectories are both copied."""
        # given:
        input_dir = tmp_path / 'input'
        output_dir = tmp_path / 'output'
        _create_media_file(input_dir / 'sub1' / 'photo1.jpg')
        _create_media_file(input_dir / 'sub2' / 'photo2.jpg', content=b'different content')
        output_dir.mkdir()
        monkeypatch.setattr('aidsoid_photo_organiser.main.detect_taken_time', lambda _: datetime(2019, 1, 1))

        # when:
        result = process_files(
            input_dir=input_dir,
            output_dir=output_dir,
            valid_extensions=VALID_EXTENSIONS,
            use_hardlinks=False,
        )

        # then:
        # and: both media files are copied, no duplicates or not_copied
        assert len(result['copied']) == 2
        assert len(result['duplicates']) == 0
        assert len(result['not_copied']) == 0

        # and: both media files are in correct location
        assert (output_dir / '2019' / '01' / 'photo1.jpg').exists()
        assert (output_dir / '2019' / '01' / 'photo2.jpg').exists()

    def test__two_duplicate_media_in_subdirs__one_copied_one_duplicate(self, tmp_path, monkeypatch):
        """Identical media files in different subdirectories — first copied, second is duplicate."""
        # given:
        input_dir = tmp_path / 'input'
        output_dir = tmp_path / 'output'
        same_content = b'\xff\xd8\xff\xe0' + b'\x00' * 100
        _create_media_file(input_dir / 'sub1' / 'photo.jpg', content=same_content)
        _create_media_file(input_dir / 'sub2' / 'photo.jpg', content=same_content)
        output_dir.mkdir()
        monkeypatch.setattr('aidsoid_photo_organiser.main.detect_taken_time', lambda _: datetime(2019, 1, 1))

        # when:
        result = process_files(
            input_dir=input_dir,
            output_dir=output_dir,
            valid_extensions=VALID_EXTENSIONS,
            use_hardlinks=False,
        )

        # then:
        # and: one media file is copied, the other is marked as duplicate, no not_copied
        assert len(result['copied']) == 1
        assert len(result['duplicates']) == 1
        assert len(result['not_copied']) == 0

        # and: media is in correct location
        assert (output_dir / '2019' / '01' / 'photo.jpg').exists()

    def test__two_same_name_media_in_subdirs__both_copied_second_with_uuid(self, tmp_path, monkeypatch):
        """Two media files with same name but different content — second gets UUID suffix."""
        # given:
        input_dir = tmp_path / 'input'
        output_dir = tmp_path / 'output'
        _create_media_file(input_dir / 'sub1' / 'photo.jpg')
        _create_media_file(input_dir / 'sub2' / 'photo.jpg', content=b'different content')
        output_dir.mkdir()
        monkeypatch.setattr('aidsoid_photo_organiser.main.detect_taken_time', lambda _: datetime(2019, 1, 1))

        class FakeUUID:
            hex = 'abc123'

        monkeypatch.setattr('aidsoid_photo_organiser.main.uuid.uuid4', lambda: FakeUUID())

        # when:
        result = process_files(
            input_dir=input_dir,
            output_dir=output_dir,
            valid_extensions=VALID_EXTENSIONS,
            use_hardlinks=False,
        )

        # then:
        # and: both media files are copied, no duplicates or not_copied
        assert len(result['copied']) == 2
        assert len(result['duplicates']) == 0
        assert len(result['not_copied']) == 0

        # and: first is copied as-is, second gets UUID suffix
        assert (output_dir / '2019' / '01' / 'photo.jpg').exists()
        assert (output_dir / '2019' / '01' / 'photo_abc123.jpg').exists()

    def test__single_orphan_metadata__not_copied(self, tmp_path):
        """Orphan metadata without any media file goes to not_copied."""
        # given:
        input_dir = tmp_path / 'input'
        output_dir = tmp_path / 'output'
        _create_metadata_json(input_dir / 'deleted_photo.jpg', timestamp='1546300800')
        output_dir.mkdir()

        # when:
        result = process_files(
            input_dir=input_dir,
            output_dir=output_dir,
            valid_extensions=VALID_EXTENSIONS,
            use_hardlinks=False,
        )

        # then:
        # and: no media is copied, no duplicates, but one not_copied for the orphan metadata
        assert len(result['copied']) == 0
        assert len(result['duplicates']) == 0
        assert len(result['not_copied']) == 1

        # and: metadata file is not in output
        assert not list(output_dir.rglob('*.json'))

    def test__non_media_file__not_copied(self, tmp_path):
        """Non-media, non-metadata file goes to not_copied."""
        # given:
        input_dir = tmp_path / 'input'
        output_dir = tmp_path / 'output'
        input_dir.mkdir()
        (input_dir / 'readme.txt').write_text('hello')
        output_dir.mkdir()

        # when:
        result = process_files(
            input_dir=input_dir,
            output_dir=output_dir,
            valid_extensions=VALID_EXTENSIONS,
            use_hardlinks=False,
        )

        # then:
        # and: file is not copied, no duplicates
        assert len(result['copied']) == 0
        assert len(result['duplicates']) == 0
        assert len(result['not_copied']) == 1

        # and: file is not in output
        assert not list(output_dir.rglob('readme.txt'))

    def test__media_in_ignored_dir__silently_skipped(self, tmp_path, monkeypatch):
        """Media file inside an ignored directory is silently skipped — not copied, not counted."""
        # given:
        input_dir = tmp_path / 'input'
        output_dir = tmp_path / 'output'
        ignored_dir = sorted(IGNORED_DIRS)[0]
        _create_media_file(input_dir / ignored_dir / 'photo.jpg')
        output_dir.mkdir()
        monkeypatch.setattr('aidsoid_photo_organiser.main.detect_taken_time', lambda _: datetime(2019, 1, 1))

        # when:
        result = process_files(
            input_dir=input_dir,
            output_dir=output_dir,
            valid_extensions=VALID_EXTENSIONS,
            use_hardlinks=False,
        )

        # then:
        # and: file is not in any result category
        assert len(result['copied']) == 0
        assert len(result['duplicates']) == 0
        assert len(result['not_copied']) == 0

        # and: nothing is in output
        assert not list(output_dir.rglob('*'))

    def test__two_same_name_media_with_metadata__second_media_and_metadata_get_uuid(self, tmp_path, monkeypatch):
        """Two same-name media with metadata — second media and its metadata both get UUID suffix."""
        # given:
        input_dir = tmp_path / 'input'
        output_dir = tmp_path / 'output'
        media1 = _create_media_file(input_dir / 'sub1' / 'photo.jpg')
        _create_metadata_json(media1, timestamp='1546300800')  # 2019-01-01
        media2 = _create_media_file(input_dir / 'sub2' / 'photo.jpg', content=b'different content')
        _create_metadata_json(media2, timestamp='1546300800')  # 2019-01-01
        output_dir.mkdir()

        class FakeUUID:
            hex = 'abc123'

        monkeypatch.setattr('aidsoid_photo_organiser.main.uuid.uuid4', lambda: FakeUUID())

        # when:
        result = process_files(
            input_dir=input_dir,
            output_dir=output_dir,
            valid_extensions=VALID_EXTENSIONS,
            use_hardlinks=False,
        )

        # then:
        # and: both media and both metadata are copied
        assert len(result['copied']) == 4
        assert len(result['duplicates']) == 0
        assert len(result['not_copied']) == 0

        # and: first media and its metadata are as-is
        assert (output_dir / '2019' / '01' / 'photo.jpg').exists()
        assert (output_dir / '2019' / '01' / 'photo.jpg.supplemental-metadata.json').exists()

        # and: second media and its metadata both have UUID suffix
        assert (output_dir / '2019' / '01' / 'photo_abc123.jpg').exists()
        assert (output_dir / '2019' / '01' / 'photo.jpg.supplemental-metadata_abc123.json').exists()

    def test__two_duplicate_media_with_metadata__both_media_and_metadata_duplicate(self, tmp_path):
        """Two identical media with identical metadata — second media and metadata are duplicates."""
        # given:
        input_dir = tmp_path / 'input'
        output_dir = tmp_path / 'output'
        same_content = b'\xff\xd8\xff\xe0' + b'\x00' * 100
        media1 = _create_media_file(input_dir / 'sub1' / 'photo.jpg', content=same_content)
        _create_metadata_json(media1, timestamp='1546300800')  # 2019-01-01
        media2 = _create_media_file(input_dir / 'sub2' / 'photo.jpg', content=same_content)
        _create_metadata_json(media2, timestamp='1546300800')  # 2019-01-01
        output_dir.mkdir()

        # when:
        result = process_files(
            input_dir=input_dir,
            output_dir=output_dir,
            valid_extensions=VALID_EXTENSIONS,
            use_hardlinks=False,
        )

        # then:
        # and: first media and metadata are copied, second media and metadata are duplicates
        assert len(result['copied']) == 2
        assert len(result['duplicates']) == 2
        assert len(result['not_copied']) == 0

        # and: only one copy of media and metadata in output
        assert (output_dir / '2019' / '01' / 'photo.jpg').exists()
        assert (output_dir / '2019' / '01' / 'photo.jpg.supplemental-metadata.json').exists()
        assert len(list((output_dir / '2019' / '01').iterdir())) == 2

    def test__two_media_different_dates__sorted_into_different_dirs(self, tmp_path, monkeypatch):
        """Two media with different dates are sorted into separate YYYY/MM directories."""
        # given:
        input_dir = tmp_path / 'input'
        output_dir = tmp_path / 'output'
        _create_media_file(input_dir / 'january.jpg')
        _create_media_file(input_dir / 'november.jpg', content=b'different content')
        output_dir.mkdir()

        dates = {
            'january.jpg': datetime(2019, 1, 15),
            'november.jpg': datetime(2021, 11, 3),
        }
        monkeypatch.setattr('aidsoid_photo_organiser.main.detect_taken_time', lambda p: dates[p.name])

        # when:
        result = process_files(
            input_dir=input_dir,
            output_dir=output_dir,
            valid_extensions=VALID_EXTENSIONS,
            use_hardlinks=False,
        )

        # then:
        # and: both are copied, no duplicates or not_copied
        assert len(result['copied']) == 2
        assert len(result['duplicates']) == 0
        assert len(result['not_copied']) == 0

        # and: each media is in its own YYYY/MM directory
        assert (output_dir / '2019' / '01' / 'january.jpg').exists()
        assert (output_dir / '2021' / '11' / 'november.jpg').exists()

    def test__truncation_collision__metadata_counted_once(self, tmp_path):
        """Two media whose truncated names collide on the same metadata — metadata counted once."""
        # given: two media files with long names that truncate to the same 46-char metadata prefix
        # "aaaaaa...a_CO.jpeg" and "aaaaaa...a_COV.jpg" both truncate to "aaaaaa...a_CO"
        input_dir = tmp_path / 'input'
        output_dir = tmp_path / 'output'
        # 36 chars prefix + suffix makes total > 46 after ".supplemental-metadata" is appended
        prefix = 'a' * 36
        media1 = _create_media_file(input_dir / f'{prefix}_CO.jpeg')
        media2 = _create_media_file(input_dir / f'{prefix}_COV.jpg', content=b'different content')  # noqa: F841
        # create metadata only for media1 — but truncation makes media2 find the same file
        _create_metadata_json(media1, timestamp='1546300800')  # 2019-01-01
        output_dir.mkdir()

        # when:
        result = process_files(
            input_dir=input_dir,
            output_dir=output_dir,
            valid_extensions=VALID_EXTENSIONS,
            use_hardlinks=False,
        )

        # then:
        # and: both media copied, metadata counted exactly once, no duplicates
        assert len(result['copied']) == 3  # 2 media + 1 metadata
        assert len(result['duplicates']) == 0
        assert len(result['not_copied']) == 0
