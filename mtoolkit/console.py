# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright (c) 2010-2011, GEM Foundation.
#
# MToolkit is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# only, as published by the Free Software Foundation.
#
# MToolkit is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License version 3 for more details
# (a copy is included in the LICENSE file that accompanied this code).
#
# You should have received a copy of the GNU Lesser General Public License
# version 3 along with MToolkit. If not, see
# <http://www.gnu.org/licenses/lgpl-3.0.txt> for a copy of the LGPLv3 License.

"""
A set of utility functions for cmdline
"""

import os
import sys
import argparse
import logging


def build_cmd_parser():
    """
    Create a simple parser for cmdline
    """

    parser = argparse.ArgumentParser(prog='MToolkit')
    parser.add_argument('-i', '--input-file',
                        dest='input_file',
                        nargs=1,
                        help="""Specify the configuration
                        file (i.e. config.yml)""")

    parser.add_argument('-d', '--detailed',
                        help="""Show detailed information
                        about the workflow
                        """,
                        action='store_true')

    parser.add_argument('-v', '--version',
                        action='version',
                        version="%(prog)s 0.1")
    return parser


def cmd_line():
    """
    Return cmdline input argument
    after checking the proper input
    has been given.
    """

    parser = build_cmd_parser()
    args = None
    if len(sys.argv) == 1:
        parser.print_help()
    else:
        args = parser.parse_args()
        if not os.path.exists(args.input_file[0]):
            print 'Error: non existent input file\n'
            parser.print_help()

    return args


def build_logger(logging_level):
    """
    Build a custom logger which provides
    log data to the cmdline and in a log_file
    """

    logger = logging.getLogger('mt_logger')
    logger.setLevel(logging_level)

    formatter = logging.Formatter('%(message)s\n')

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if logging_level < logging.INFO:
        logfile_handler = logging.FileHandler('debug.log')
        logfile_handler.setLevel(logging_level)
        logfile_handler.setFormatter(formatter)
        logger.addHandler(logfile_handler)
