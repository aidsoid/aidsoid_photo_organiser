# Copyright (c) 2026 Alexey Doroshenko <aidsoid@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later OR Commercial
# See LICENSE and COMMERCIAL_LICENSE.md for details.

"""Unit tests for file operation helpers."""

import os
from pathlib import Path

import pytest

from aidsoid_photo_organiser.file_operations import (
    CopyFileError,
    CreateHardlinkError,
    CreateHardlinkOrCopyFileError,
    are_files_identical,
    compare_directories,
    copy_file,
    copy_file_or_create_hardlink,
    create_hardlink,
    get_file_hash,
)


def _create_file(path: Path, content: str = 'hello') -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


class TestCopyFile:
    """Tests for `copy_file` behavior."""

    def test__copy_file__valid_src_and_dst__copies_content(self, tmp_path):
        """Copies file content to the destination."""
        # given:
        src = _create_file(tmp_path / 'src.txt', 'data')
        dst = tmp_path / 'dst.txt'

        # when:
        copy_file(src, dst)

        # then:
        assert dst.exists()
        assert dst.read_text() == 'data'

    def test__copy_file__valid_src__preserves_metadata(self, tmp_path):
        """Preserves modification time when copying."""
        # given:
        src = _create_file(tmp_path / 'src.txt')
        dst = tmp_path / 'dst.txt'

        # when:
        copy_file(src, dst)

        # then:
        assert src.stat().st_mtime == pytest.approx(dst.stat().st_mtime, abs=1)

    def test__copy_file__missing_source__raises_copy_file_error(self, tmp_path):
        """Raises CopyFileError when source file does not exist."""
        # given:
        src = tmp_path / 'nonexistent.txt'
        dst = tmp_path / 'dst.txt'

        # when/then:
        with pytest.raises(CopyFileError, match='File not found'):
            copy_file(src, dst)

    def test__copy_file__missing_destination_dir__raises_copy_file_error(self, tmp_path):
        """Raises CopyFileError when destination directory does not exist."""
        # given:
        src = _create_file(tmp_path / 'src.txt')
        dst = tmp_path / 'no_such_dir' / 'dst.txt'

        # when/then:
        with pytest.raises(CopyFileError):
            copy_file(src, dst)


class TestCreateHardlink:
    """Tests for `create_hardlink` behavior."""

    def test__create_hardlink__valid_src_and_dst__shares_inode(self, tmp_path):
        """Creates a hardlink sharing the same inode as the source."""
        # given:
        src = _create_file(tmp_path / 'src.txt', 'data')
        dst = tmp_path / 'link.txt'

        # when:
        create_hardlink(src, dst)

        # then:
        assert dst.exists()
        assert dst.read_text() == 'data'
        assert os.stat(src).st_ino == os.stat(dst).st_ino

    def test__create_hardlink__missing_source__raises_create_hardlink_error(self, tmp_path):
        """Raises CreateHardlinkError when source file does not exist."""
        # given:
        src = tmp_path / 'nonexistent.txt'
        dst = tmp_path / 'link.txt'

        # when/then:
        with pytest.raises(CreateHardlinkError, match='File not found'):
            create_hardlink(src, dst)

    def test__create_hardlink__destination_exists__raises_create_hardlink_error(self, tmp_path):
        """Raises CreateHardlinkError when destination file already exists."""
        # given:
        src = _create_file(tmp_path / 'src.txt')
        dst = _create_file(tmp_path / 'dst.txt')

        # when/then:
        with pytest.raises(CreateHardlinkError):
            create_hardlink(src, dst)


class TestCopyFileOrCreateHardlink:
    """Tests for `copy_file_or_create_hardlink` behavior."""

    def test__copy_file_or_create_hardlink__use_hardlinks_true__creates_hardlink(self, tmp_path):
        """Creates a hardlink when use_hardlinks is True."""
        # given:
        src = _create_file(tmp_path / 'src.txt', 'data')
        dst = tmp_path / 'dst.txt'

        # when:
        copy_file_or_create_hardlink(src, dst, use_hardlinks=True, is_metadata_file=False)

        # then:
        assert dst.exists()
        assert os.stat(src).st_ino == os.stat(dst).st_ino

    def test__copy_file_or_create_hardlink__use_hardlinks_false__copies_file(self, tmp_path):
        """Copies the file when use_hardlinks is False."""
        # given:
        src = _create_file(tmp_path / 'src.txt', 'data')
        dst = tmp_path / 'dst.txt'

        # when:
        copy_file_or_create_hardlink(src, dst, use_hardlinks=False, is_metadata_file=False)

        # then:
        assert dst.exists()
        assert dst.read_text() == 'data'
        assert os.stat(src).st_ino != os.stat(dst).st_ino

    def test__copy_file_or_create_hardlink__metadata_file_flag__does_not_affect_result(self, tmp_path):
        """Copies the file regardless of is_metadata_file flag value."""
        # given:
        src = _create_file(tmp_path / 'src.txt', 'meta')
        dst = tmp_path / 'dst.txt'

        # when:
        copy_file_or_create_hardlink(src, dst, use_hardlinks=False, is_metadata_file=True)

        # then:
        assert dst.read_text() == 'meta'

    def test__copy_file_or_create_hardlink__hardlink_fails__raises_error(self, tmp_path):
        """Propagates CreateHardlinkOrCopyFileError when hardlink creation fails."""
        # given:
        src = tmp_path / 'nonexistent.txt'
        dst = tmp_path / 'dst.txt'

        # when/then:
        with pytest.raises(CreateHardlinkOrCopyFileError):
            copy_file_or_create_hardlink(src, dst, use_hardlinks=True, is_metadata_file=False)

    def test__copy_file_or_create_hardlink__copy_fails__raises_error(self, tmp_path):
        """Propagates CreateHardlinkOrCopyFileError when file copy fails."""
        # given:
        src = tmp_path / 'nonexistent.txt'
        dst = tmp_path / 'dst.txt'

        # when/then:
        with pytest.raises(CreateHardlinkOrCopyFileError):
            copy_file_or_create_hardlink(src, dst, use_hardlinks=False, is_metadata_file=False)


class TestGetFileHash:
    """Tests for `get_file_hash` behavior."""

    def test__get_file_hash__same_file_called_twice__returns_same_hash(self, tmp_path):
        """Returns the same hash for the same file on repeated calls."""
        # given:
        f = _create_file(tmp_path / 'a.txt', 'hello world')

        # when:
        hash1 = get_file_hash(f)
        hash2 = get_file_hash(f)

        # then:
        assert hash1 == hash2

    def test__get_file_hash__identical_content__returns_same_hash(self, tmp_path):
        """Returns identical hashes for files with identical content."""
        # given:
        f1 = _create_file(tmp_path / 'a.txt', 'same')
        f2 = _create_file(tmp_path / 'b.txt', 'same')

        # when:
        hash1 = get_file_hash(f1)
        hash2 = get_file_hash(f2)

        # then:
        assert hash1 == hash2

    def test__get_file_hash__different_content__returns_different_hash(self, tmp_path):
        """Returns different hashes for files with different content."""
        # given:
        f1 = _create_file(tmp_path / 'a.txt', 'aaa')
        f2 = _create_file(tmp_path / 'b.txt', 'bbb')

        # when:
        hash1 = get_file_hash(f1)
        hash2 = get_file_hash(f2)

        # then:
        assert hash1 != hash2

    def test__get_file_hash__empty_file__returns_valid_hash_string(self, tmp_path):
        """Returns a valid hash string for an empty file."""
        # given:
        f = _create_file(tmp_path / 'empty.txt', '')

        # when:
        h = get_file_hash(f)

        # then:
        assert isinstance(h, str)
        assert len(h) > 0

    def test__get_file_hash__nonexistent_file__raises_os_error(self, tmp_path):
        """Raises OSError when the file does not exist."""
        # given:
        f = tmp_path / 'no_such_file.txt'

        # when/then:
        with pytest.raises(OSError):
            get_file_hash(f)


class TestAreFilesIdentical:
    """Tests for `are_files_identical` behavior."""

    def test__are_files_identical__same_content__returns_true(self, tmp_path):
        """Returns True for two files with the same content."""
        # given:
        f1 = _create_file(tmp_path / 'a.txt', 'same content')
        f2 = _create_file(tmp_path / 'b.txt', 'same content')

        # when:
        result = are_files_identical(f1, f2)

        # then:
        assert result is True

    def test__are_files_identical__different_content__returns_false(self, tmp_path):
        """Returns False for two files with different content."""
        # given:
        f1 = _create_file(tmp_path / 'a.txt', 'content A')
        f2 = _create_file(tmp_path / 'b.txt', 'content B')

        # when:
        result = are_files_identical(f1, f2)

        # then:
        assert result is False

    def test__are_files_identical__different_sizes__returns_false(self, tmp_path):
        """Returns False immediately when file sizes differ without hashing."""
        # given:
        f1 = _create_file(tmp_path / 'a.txt', 'short')
        f2 = _create_file(tmp_path / 'b.txt', 'this is much longer content')

        # when:
        result = are_files_identical(f1, f2)

        # then:
        assert result is False

    def test__are_files_identical__same_path__returns_true(self, tmp_path):
        """Returns True when both arguments point to the same file."""
        # given:
        f = _create_file(tmp_path / 'a.txt', 'data')

        # when:
        result = are_files_identical(f, f)

        # then:
        assert result is True

    def test__are_files_identical__identical_binary_files__returns_true(self, tmp_path):
        """Returns True for identical binary files."""
        # given:
        f1 = tmp_path / 'a.bin'
        f2 = tmp_path / 'b.bin'
        data = bytes(range(256))
        f1.write_bytes(data)
        f2.write_bytes(data)

        # when:
        result = are_files_identical(f1, f2)

        # then:
        assert result is True

    def test__are_files_identical__binary_files_differ_by_one_byte__returns_false(self, tmp_path):
        """Returns False when binary files differ by a single byte."""
        # given:
        f1 = tmp_path / 'a.bin'
        f2 = tmp_path / 'b.bin'
        data = bytes(range(256))
        f1.write_bytes(data)
        f2.write_bytes(data[:-1] + b'\x00')

        # when:
        result = are_files_identical(f1, f2)

        # then:
        assert result is False


class TestCompareDirectories:
    """Tests for `compare_directories` behavior."""

    def test__compare_directories__identical_dirs__returns_empty_list(self, tmp_path):
        """Returns empty list when both directories have the same files."""
        # given:
        dir1 = tmp_path / 'dir1'
        dir2 = tmp_path / 'dir2'
        _create_file(dir1 / 'a.txt', 'aaa')
        _create_file(dir2 / 'a.txt', 'aaa')

        # when:
        missing = compare_directories(dir1, dir2)

        # then:
        assert missing == []

    def test__compare_directories__file_missing_in_dir2__returns_missing_file(self, tmp_path):
        """Returns files present in dir1 but absent in dir2."""
        # given:
        dir1 = tmp_path / 'dir1'
        dir2 = tmp_path / 'dir2'
        _create_file(dir1 / 'a.txt', 'aaa')
        _create_file(dir1 / 'b.txt', 'bbb')
        _create_file(dir2 / 'a.txt', 'aaa')

        # when:
        missing = compare_directories(dir1, dir2)

        # then:
        assert len(missing) == 1
        assert missing[0].name == 'b.txt'

    def test__compare_directories__same_content_different_name__returns_empty_list(self, tmp_path):
        """Does not report a file as missing if its content exists under a different name."""
        # given:
        dir1 = tmp_path / 'dir1'
        dir2 = tmp_path / 'dir2'
        _create_file(dir1 / 'original.txt', 'content')
        _create_file(dir2 / 'renamed.txt', 'content')

        # when:
        missing = compare_directories(dir1, dir2)

        # then:
        assert missing == []

    def test__compare_directories__same_name_different_content__reports_as_missing(self, tmp_path):
        """Reports a file as missing when same-named file has different content."""
        # given:
        dir1 = tmp_path / 'dir1'
        dir2 = tmp_path / 'dir2'
        _create_file(dir1 / 'a.txt', 'version1')
        _create_file(dir2 / 'a.txt', 'version2')

        # when:
        missing = compare_directories(dir1, dir2)

        # then:
        assert len(missing) == 1

    def test__compare_directories__eadir_present__excludes_eadir_files(self, tmp_path):
        """Excludes files inside @eaDir directories from comparison."""
        # given:
        dir1 = tmp_path / 'dir1'
        dir2 = tmp_path / 'dir2'
        dir2.mkdir()
        _create_file(dir1 / 'a.txt', 'aaa')
        _create_file(dir1 / '@eaDir' / 'thumb.jpg', 'thumb')

        # when:
        missing = compare_directories(dir1, dir2)

        # then:
        assert len(missing) == 1
        assert all('@eaDir' not in f.parts for f in missing)

    def test__compare_directories__nested_subdirs__matches_by_hash(self, tmp_path):
        """Matches files by hash across different nested directory structures."""
        # given:
        dir1 = tmp_path / 'dir1'
        dir2 = tmp_path / 'dir2'
        _create_file(dir1 / 'sub' / 'deep' / 'a.txt', 'nested')
        _create_file(dir2 / 'other' / 'a.txt', 'nested')

        # when:
        missing = compare_directories(dir1, dir2)

        # then:
        assert missing == []

    def test__compare_directories__both_dirs_empty__returns_empty_list(self, tmp_path):
        """Returns empty list when both directories are empty."""
        # given:
        dir1 = tmp_path / 'dir1'
        dir2 = tmp_path / 'dir2'
        dir1.mkdir()
        dir2.mkdir()

        # when:
        missing = compare_directories(dir1, dir2)

        # then:
        assert missing == []

    def test__compare_directories__dir2_empty__returns_all_dir1_files(self, tmp_path):
        """Returns all dir1 files when dir2 is empty."""
        # given:
        dir1 = tmp_path / 'dir1'
        dir2 = tmp_path / 'dir2'
        _create_file(dir1 / 'a.txt', 'aaa')
        _create_file(dir1 / 'b.txt', 'bbb')
        dir2.mkdir()

        # when:
        missing = compare_directories(dir1, dir2)

        # then:
        assert len(missing) == 2
