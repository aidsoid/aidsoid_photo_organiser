# Copyright (c) 2026 Alexey Doroshenko <aidsoid@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later OR Commercial
# See LICENSE and COMMERCIAL_LICENSE.md for details.

"""Extract capture date from common filename patterns used by cameras and devices."""

import re
from datetime import datetime
from pathlib import Path


def _find_embedded_datetime(file_name: str) -> datetime | None:
    """
    Search for a date+time pattern anywhere in the filename.

    Format: YYYY[s]MM[s]DD<s>HH[s]MM[s]SS
        - [s] — optional separator (dash, underscore, dot, or space)
        - <s> — mandatory separator (same set)

    Covers (examples):
        - 20130716_184913              (compact date, underscore, compact time)
        - 20130716-184913              (compact date, dash, compact time)
        - 2021-03-15 14.20.30          (separated date, space, dot-separated time)
        - 2021-03-15_14-20-30          (separated date, underscore, dash-separated time)
        - 2021-03-15-14-20-30          (all dashes)
    """
    match = re.search(
        r"""
        (?<!\d)                # not preceded by a digit
        (\d{4})                # year
        [-_. ]?                # optional separator
        (0[1-9]|1[0-2])        # month  (01-12)
        [-_. ]?                # optional separator
        (0[1-9]|[12]\d|3[01])  # day    (01-31)
        [-_. ]                 # separator (between date and time)
        (\d{2})                # hour
        [-_. ]?                # optional separator
        (\d{2})                # minute
        [-_. ]?                # optional separator
        (\d{2})                # second
        (?!\d)                 # not followed by a digit
    """,
        file_name,
        re.VERBOSE,
    )
    if match:
        try:
            return datetime(
                int(match.group(1)),
                int(match.group(2)),
                int(match.group(3)),
                int(match.group(4)),
                int(match.group(5)),
                int(match.group(6)),
            )
        except ValueError:
            return None
    return None


def _find_embedded_date(file_name: str) -> datetime | None:
    """
    Search for a date-only pattern anywhere in the filename. Time is set to 00:00:00.

    Format: YYYY[s]MM[s]DD
        - [s] — optional separator (dash, underscore, dot, or space)

    Covers (examples):
        - 2014-06-30   (dashes)
        - 2014_06_30   (underscores)
        - 2014.06.30   (dots)
        - 2014 06 30   (spaces)
        - 20140630     (compact)
    """
    match = re.search(
        r"""
        (?<!\d)                # not preceded by a digit
        (\d{4})                # year
        [-_. ]?                # optional separator
        (0[1-9]|1[0-2])        # month  (01-12)
        [-_. ]?                # optional separator
        (0[1-9]|[12]\d|3[01])  # day    (01-31)
        (?!\d)                 # not followed by a digit
    """,
        file_name,
        re.VERBOSE,
    )
    if match:
        try:
            return datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        except ValueError:
            return None
    return None


def extract_datetime_from_filename(file_path: Path) -> datetime | None:
    """
    Extract the capture date and time from a media filename.

    Tries datetime first (date + time), then falls back to date only (time set to 00:00:00).
    Both functions accept optional separators between components and use strict
    month/day validation in regex.

    :param file_path: Path to the media file.
    :return: The extracted datetime, or None if no pattern matches.
    """
    file_name = file_path.stem
    return _find_embedded_datetime(file_name) or _find_embedded_date(file_name)
