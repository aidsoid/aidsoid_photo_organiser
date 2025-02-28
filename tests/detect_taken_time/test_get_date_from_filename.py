# Copyright (c) 2026 Alexey Doroshenko <aidsoid@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later OR Commercial
# See LICENSE and COMMERCIAL_LICENSE.md for details.

"""Unit tests for extract_datetime_from_filename."""

from datetime import datetime
from pathlib import Path

from aidsoid_photo_organiser.detect_taken_time.get_date_from_filename import extract_datetime_from_filename


class TestExtractDatetimeFromFilename:
    """Tests for `extract_datetime_from_filename`."""

    # --- Date + time patterns ---

    def test__extract_datetime_from_filename__vid_prefix__success(self):
        """VID_ prefix parses date and time correctly."""
        # given:
        file_path = Path('VID_20131229_223028.mkv')
        expected = datetime(year=2013, month=12, day=29, hour=22, minute=30, second=28)

        # when:
        result = extract_datetime_from_filename(file_path=file_path)

        # then:
        assert result == expected

    def test__extract_datetime_from_filename__img_prefix__success(self):
        """IMG_ prefix parses date and time correctly."""
        # given:
        file_path = Path('IMG_20200315_142030.jpg')
        expected = datetime(year=2020, month=3, day=15, hour=14, minute=20, second=30)

        # when:
        result = extract_datetime_from_filename(file_path=file_path)

        # then:
        assert result == expected

    def test__extract_datetime_from_filename__pxl_prefix__success(self):
        """PXL_ prefix (Google Pixel) parses date and time correctly."""
        # given:
        file_path = Path('PXL_20220801_190045.jpg')
        expected = datetime(year=2022, month=8, day=1, hour=19, minute=0, second=45)

        # when:
        result = extract_datetime_from_filename(file_path=file_path)

        # then:
        assert result == expected

    def test__extract_datetime_from_filename__pano_prefix__success(self):
        """PANO_ prefix (Android panorama) parses date and time correctly."""
        # given:
        file_path = Path('PANO_20180610_153020.jpg')
        expected = datetime(year=2018, month=6, day=10, hour=15, minute=30, second=20)

        # when:
        result = extract_datetime_from_filename(file_path=file_path)

        # then:
        assert result == expected

    def test__extract_datetime_from_filename__dji_prefix__success(self):
        """DJI_ prefix (DJI drone) parses date and time correctly."""
        # given:
        file_path = Path('DJI_20230415_120000.mp4')
        expected = datetime(year=2023, month=4, day=15, hour=12, minute=0, second=0)

        # when:
        result = extract_datetime_from_filename(file_path=file_path)

        # then:
        assert result == expected

    def test__extract_datetime_from_filename__mvimg_prefix__success(self):
        """MVIMG_ prefix (Google Motion Photo) parses date and time correctly."""
        # given:
        file_path = Path('MVIMG_20200101_183000.jpg')
        expected = datetime(year=2020, month=1, day=1, hour=18, minute=30, second=0)

        # when:
        result = extract_datetime_from_filename(file_path=file_path)

        # then:
        assert result == expected

    def test__extract_datetime_from_filename__burst_prefix__success(self):
        """BURST_ prefix (burst/serial shot) parses date and time correctly."""
        # given:
        file_path = Path('BURST_20190501_093000.jpg')
        expected = datetime(year=2019, month=5, day=1, hour=9, minute=30, second=0)

        # when:
        result = extract_datetime_from_filename(file_path=file_path)

        # then:
        assert result == expected

    def test__extract_datetime_from_filename__screenshot_android__success(self):
        """Android screenshot format (Screenshot_YYYYMMDD-HHMMSS) parses correctly."""
        # given:
        file_path = Path('Screenshot_20210315-142030.png')
        expected = datetime(year=2021, month=3, day=15, hour=14, minute=20, second=30)

        # when:
        result = extract_datetime_from_filename(file_path=file_path)

        # then:
        assert result == expected

    def test__extract_datetime_from_filename__screenshot_samsung__success(self):
        """Samsung screenshot format (Screenshot_YYYY-MM-DD-HH-MM-SS) parses correctly."""
        # given:
        file_path = Path('Screenshot_2021-03-15-14-20-30.png')
        expected = datetime(year=2021, month=3, day=15, hour=14, minute=20, second=30)

        # when:
        result = extract_datetime_from_filename(file_path=file_path)

        # then:
        assert result == expected

    def test__extract_datetime_from_filename__ios_export_space_dots__success(self):
        """IOS export format (YYYY-MM-DD HH.MM.SS) parses date and time correctly."""
        # given:
        file_path = Path('2021-03-15 14.20.30.jpg')
        expected = datetime(year=2021, month=3, day=15, hour=14, minute=20, second=30)

        # when:
        result = extract_datetime_from_filename(file_path=file_path)

        # then:
        assert result == expected

    def test__extract_datetime_from_filename__various_apps_underscore_dashes__success(self):
        """Various apps format (YYYY-MM-DD_HH-MM-SS) parses date and time correctly."""
        # given:
        file_path = Path('2021-03-15_14-20-30.jpg')
        expected = datetime(year=2021, month=3, day=15, hour=14, minute=20, second=30)

        # when:
        result = extract_datetime_from_filename(file_path=file_path)

        # then:
        assert result == expected

    # --- Date only patterns ---

    def test__extract_datetime_from_filename__whatsapp_img__date_only_with_midnight_time(self):
        """WhatsApp IMG- filename returns date with time set to 00:00:00."""
        # given:
        file_path = Path('IMG-20190825-WA0012.jpg')
        expected = datetime(year=2019, month=8, day=25, hour=0, minute=0, second=0)

        # when:
        result = extract_datetime_from_filename(file_path=file_path)

        # then:
        assert result == expected

    def test__extract_datetime_from_filename__whatsapp_vid__date_only_with_midnight_time(self):
        """WhatsApp VID- filename returns date with time set to 00:00:00."""
        # given:
        file_path = Path('VID-20190825-WA0003.mp4')
        expected = datetime(year=2019, month=8, day=25, hour=0, minute=0, second=0)

        # when:
        result = extract_datetime_from_filename(file_path=file_path)

        # then:
        assert result == expected

    def test__extract_datetime_from_filename__embedded_dashes__date_only_with_midnight_time(self):
        """Bare ISO date (YYYY-MM-DD) returns date with time set to 00:00:00."""
        # given:
        file_path = Path('2014-06-30.jpg')
        expected = datetime(year=2014, month=6, day=30, hour=0, minute=0, second=0)

        # when:
        result = extract_datetime_from_filename(file_path=file_path)

        # then:
        assert result == expected

    def test__extract_datetime_from_filename__embedded_dashes_with_suffix__date_only_with_midnight_time(self):
        """ISO date with duplicate suffix (YYYY-MM-DD(N)) returns date with time set to 00:00:00."""
        # given:
        file_path = Path('2014-07-28(2).jpg')
        expected = datetime(year=2014, month=7, day=28, hour=0, minute=0, second=0)

        # when:
        result = extract_datetime_from_filename(file_path=file_path)

        # then:
        assert result == expected

    def test__extract_datetime_from_filename__embedded_underscores__date_only_with_midnight_time(self):
        """Date with underscores (YYYY_MM_DD) returns date with time set to 00:00:00."""
        # given:
        file_path = Path('photo_2014_06_30_edit.jpg')
        expected = datetime(year=2014, month=6, day=30, hour=0, minute=0, second=0)

        # when:
        result = extract_datetime_from_filename(file_path=file_path)

        # then:
        assert result == expected

    def test__extract_datetime_from_filename__embedded_dots__date_only_with_midnight_time(self):
        """Date with dots (YYYY.MM.DD) returns date with time set to 00:00:00."""
        # given:
        file_path = Path('2014.06.30.jpg')
        expected = datetime(year=2014, month=6, day=30, hour=0, minute=0, second=0)

        # when:
        result = extract_datetime_from_filename(file_path=file_path)

        # then:
        assert result == expected

    def test__extract_datetime_from_filename__embedded_compact__date_only_with_midnight_time(self):
        """Compact date (YYYYMMDD) returns date with time set to 00:00:00."""
        # given:
        file_path = Path('photo_20140630.jpg')
        expected = datetime(year=2014, month=6, day=30, hour=0, minute=0, second=0)

        # when:
        result = extract_datetime_from_filename(file_path=file_path)

        # then:
        assert result == expected

    def test__extract_datetime_from_filename__embedded_compact_with_time__success(self):
        """Compact date+time (YYYYMMDD_HHMMSS) parses both date and time."""
        # given:
        file_path = Path('20130716_184913.jpg')
        expected = datetime(year=2013, month=7, day=16, hour=18, minute=49, second=13)

        # when:
        result = extract_datetime_from_filename(file_path=file_path)

        # then:
        assert result == expected

    def test__extract_datetime_from_filename__embedded_compact_with_time_and_suffix__success(self):
        """Compact date+time with suffix (YYYYMMDD_HHMMSS-edited) parses both date and time."""
        # given:
        file_path = Path('20130716_184913-edited.jpg')
        expected = datetime(year=2013, month=7, day=16, hour=18, minute=49, second=13)

        # when:
        result = extract_datetime_from_filename(file_path=file_path)

        # then:
        assert result == expected

    def test__extract_datetime_from_filename__embedded_spaces__date_only_with_midnight_time(self):
        """Date with spaces (YYYY MM DD) returns date with time set to 00:00:00."""
        # given:
        file_path = Path('2014 06 30.jpg')
        expected = datetime(year=2014, month=6, day=30, hour=0, minute=0, second=0)

        # when:
        result = extract_datetime_from_filename(file_path=file_path)

        # then:
        assert result == expected

    def test__extract_datetime_from_filename__embedded_compact_dash_with_time__success(self):
        """Compact date+time with dash separator (YYYYMMDD-HHMMSS) parses both date and time."""
        # given:
        file_path = Path('20130716-184913.jpg')
        expected = datetime(year=2013, month=7, day=16, hour=18, minute=49, second=13)

        # when:
        result = extract_datetime_from_filename(file_path=file_path)

        # then:
        assert result == expected

    def test__extract_datetime_from_filename__embedded_invalid_separated_date__returns_none(self):
        """Separated date with impossible month (13) returns None."""
        # given:
        file_path = Path('2014-13-01.jpg')

        # when:
        result = extract_datetime_from_filename(file_path=file_path)

        # then:
        assert result is None

    def test__extract_datetime_from_filename__embedded_invalid_compact_date__returns_none(self):
        """Compact date with impossible month (13) returns None."""
        # given:
        file_path = Path('photo_20141301.jpg')

        # when:
        result = extract_datetime_from_filename(file_path=file_path)

        # then:
        assert result is None

    def test__extract_datetime_from_filename__embedded_compact_with_invalid_time__falls_back_to_date(self):
        """Compact date+time with impossible hour (25) falls back to date only."""
        # given:
        file_path = Path('20130716_259999.jpg')
        expected = datetime(year=2013, month=7, day=16, hour=0, minute=0, second=0)

        # when:
        result = extract_datetime_from_filename(file_path=file_path)

        # then:
        assert result == expected

    # --- Non-matching / invalid cases ---

    def test__extract_datetime_from_filename__non_matching_filename__returns_none(self):
        """Filename with no recognised pattern returns None."""
        # given:
        file_path = Path('holiday_photo.jpg')

        # when:
        result = extract_datetime_from_filename(file_path=file_path)

        # then:
        assert result is None

    def test__extract_datetime_from_filename__invalid_date_with_prefix__returns_none(self):
        """Filename with impossible date (month 99) returns None despite valid-looking prefix."""
        # given:
        file_path = Path('VID_99991399_999999.mp4')

        # when:
        result = extract_datetime_from_filename(file_path=file_path)

        # then:
        assert result is None

    def test__extract_datetime_from_filename__feb29_non_leap_year__returns_none(self):
        """Feb 29 on a non-leap year: regex matches but datetime() rejects."""
        # given:
        file_path = Path('2023-02-29.jpg')

        # when:
        result = extract_datetime_from_filename(file_path=file_path)

        # then:
        assert result is None

    def test__extract_datetime_from_filename__feb29_leap_year__success(self):
        """Feb 29 on a leap year: valid date."""
        # given:
        file_path = Path('2024-02-29.jpg')
        expected = datetime(year=2024, month=2, day=29)

        # when:
        result = extract_datetime_from_filename(file_path=file_path)

        # then:
        assert result == expected

    def test__extract_datetime_from_filename__day31_on_30day_month__returns_none(self):
        """April 31: regex matches (day 31 is valid in regex) but datetime() rejects."""
        # given:
        file_path = Path('2023-04-31.jpg')

        # when:
        result = extract_datetime_from_filename(file_path=file_path)

        # then:
        assert result is None

    def test__extract_datetime_from_filename__long_digit_sequence__returns_none(self):
        """Long digit sequence should not produce a false match."""
        # given:
        file_path = Path('report_1234567890.pdf')

        # when:
        result = extract_datetime_from_filename(file_path=file_path)

        # then:
        assert result is None
