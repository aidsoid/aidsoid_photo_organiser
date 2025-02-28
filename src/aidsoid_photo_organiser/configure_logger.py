# Copyright (c) 2026 Alexey Doroshenko <aidsoid@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later OR Commercial
# See LICENSE and COMMERCIAL_LICENSE.md for details.

"""Logging configuration helpers for the photo organiser."""

import logging
from datetime import datetime


def configure_third_party_loggers():
    """Configure logging level for third-party libraries to WARNING to reduce log verbosity."""
    # WARNING level for third-party libs
    for lib in ['exifread', 'PIL']:
        logging.getLogger(lib).setLevel(logging.WARNING)


def configure_root_logger(verbose: bool):
    """
    Configure the root logger with console and file handlers.

    - Console handler logs messages at INFO level by default or DEBUG if `verbose` is True.
    - File handler logs all messages at DEBUG level to a log file.

    :param verbose: If True, sets the console log level to DEBUG. Otherwise, sets it to INFO.
    """
    root_logger = logging.getLogger()

    root_logger.setLevel(logging.DEBUG)

    # logging format
    console_formatter = logging.Formatter('%(message)s')
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # handler for terminal (INFO or higher)
    console_handler = logging.StreamHandler()
    # set logging level to DEBUG if --verbose is provided
    if verbose:
        console_level = logging.DEBUG
    else:
        console_level = logging.INFO
    console_handler.setLevel(console_level)
    console_handler.setFormatter(console_formatter)

    # handler for file (DEBUG or higher)
    log_filename = datetime.now().strftime('aidsoid_photo_organiser_%Y-%m-%d_%H-%M-%S.log')
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    # add handler to logger
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    if verbose:
        root_logger.debug('Verbose mode enabled. Logging level set to DEBUG.')
