# Copyright (c) 2026 Alexey Doroshenko <aidsoid@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later OR Commercial
# See LICENSE and COMMERCIAL_LICENSE.md for details.

"""Unit tests for set_file_timestamps."""

import os
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from aidsoid_photo_organiser.set_file_timestamps import set_file_timestamps


def _create_file(path: Path, content: str = 'hello') -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


class TestSetFileTimestamps:
    """Tests for `set_file_timestamps` behavior."""

    def test__set_file_timestamps__valid_file__sets_mtime(self, tmp_path):
        """Sets the modification time to the given timestamp."""
        # given:
        f = _create_file(tmp_path / 'test.txt')
        target_time = datetime(2020, 6, 15, 12, 30, 45)

        # when:
        set_file_timestamps(f, target_time)

        # then:
        assert os.path.getmtime(f) == pytest.approx(target_time.timestamp(), abs=1)

    def test__set_file_timestamps__valid_file__sets_atime(self, tmp_path):
        """Sets the access time to the given timestamp."""
        # given:
        f = _create_file(tmp_path / 'test.txt')
        target_time = datetime(2020, 6, 15, 12, 30, 45)

        # when:
        set_file_timestamps(f, target_time)

        # then:
        assert os.path.getatime(f) == pytest.approx(target_time.timestamp(), abs=1)

    def test__set_file_timestamps__nonexistent_file__raises_os_error(self, tmp_path):
        """Raises OSError when the file does not exist."""
        # given:
        f = tmp_path / 'nonexistent.txt'
        target_time = datetime(2020, 6, 15, 12, 30, 45)

        # when/then:
        with pytest.raises(OSError):
            set_file_timestamps(f, target_time)

    def test__set_file_timestamps__past_date__sets_correct_mtime(self, tmp_path):
        """Correctly handles dates far in the past."""
        # given:
        f = _create_file(tmp_path / 'test.txt')
        target_time = datetime(2000, 1, 1, 0, 0, 0)

        # when:
        set_file_timestamps(f, target_time)

        # then:
        assert os.path.getmtime(f) == pytest.approx(target_time.timestamp(), abs=1)

    def test__set_file_timestamps__called_twice__uses_last_value(self, tmp_path):
        """Calling the function twice uses the most recent timestamp."""
        # given:
        f = _create_file(tmp_path / 'test.txt')
        first_time = datetime(2020, 1, 1, 0, 0, 0)
        second_time = datetime(2022, 6, 15, 12, 0, 0)

        # when:
        set_file_timestamps(f, first_time)
        set_file_timestamps(f, second_time)

        # then:
        assert os.path.getmtime(f) == pytest.approx(second_time.timestamp(), abs=1)

    @pytest.mark.skipif(sys.platform != 'darwin', reason='macOS-only: birth time check')
    def test__set_file_timestamps__macos__sets_birth_time(self, tmp_path):
        """On macOS, setting mtime earlier than birth time also updates birth time."""
        # given:
        f = _create_file(tmp_path / 'test.txt')
        target_time = datetime(2015, 3, 20, 10, 0, 0)

        # when:
        set_file_timestamps(f, target_time)

        # then:
        stat = os.stat(f)
        assert stat.st_birthtime == pytest.approx(target_time.timestamp(), abs=1)

    def test__set_file_timestamps__does_not_use_subprocess(self, tmp_path):
        """Uses os.utime instead of subprocess for cross-platform compatibility."""
        # given:
        f = _create_file(tmp_path / 'test.txt')
        target_time = datetime(2020, 6, 15, 12, 30, 45)

        # when:
        with patch('subprocess.run') as mock_run:
            set_file_timestamps(f, target_time)

        # then:
        mock_run.assert_not_called()

    @pytest.mark.skipif(sys.platform != 'win32', reason='Windows-only: creation time via Win32 API')
    def test__set_file_timestamps__windows__calls_win32_api(self, tmp_path):
        """On Windows, additionally sets the file creation time via Win32 API."""
        # given:
        f = _create_file(tmp_path / 'test.txt')
        target_time = datetime(2020, 6, 15, 12, 30, 45)

        # when:
        set_file_timestamps(f, target_time)

        # then:
        stat = os.stat(f)
        assert stat.st_ctime == pytest.approx(target_time.timestamp(), abs=2)

    @patch('sys.platform', 'win32')
    def test__set_file_timestamps__win32_branch__calls_helper(self, tmp_path):
        """The win32 code path is invoked when sys.platform is 'win32'."""
        # given:
        f = _create_file(tmp_path / 'test.txt')
        target_time = datetime(2020, 6, 15, 12, 30, 45)
        mock_helper = MagicMock()

        # when:
        with patch('aidsoid_photo_organiser.set_file_timestamps._set_creation_time_win32', mock_helper):
            set_file_timestamps(f, target_time)

        # then:
        mock_helper.assert_called_once_with(f, target_time.timestamp())
