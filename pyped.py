#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

"""
Pyped is a command-line tool that let you process another
command output with a Python one-liner like Perl or AWK.

Like this:

    $ ps aux | py "'-'.join(x.split()[:3])" | grep 0.1

More informations: https://github.com/ksamuel/Pyped

"""


__VERSION__ = "0.2"

import sys
import os
import re
import json
import base64
import calendar
import csv
import datetime
import itertools
import random
import hashlib
import tempfile
import argparse

from os import path
from uuid import uuid1, uuid3, uuid4, uuid5
from datetime import datetime, date, time
from random import randint, random, randrange, choice
from collections import Counter, OrderedDict
from math import *


def main():

    parser = argparse.ArgumentParser(
                          description=__doc__,
                          formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("expression", help="The Python expression to evaluate",
                        nargs="?", default="x")
    parser.add_argument("-i", help="The x variable will be an iterable on the "
                                   "whole stdin. Your expression must result in "
                                   "an iterable.", action="store_true")
    parser.add_argument("-b", default="", nargs='?', metavar="expression",
                        help="Python expression to evaluate before reading "
                              "stdin. E.G: modules import")
    parser.add_argument("-v", '--version', action="store_true",
                        help="Display the script version and quit")
    parser.add_argument("--stdin-charset", nargs='?',
                        help="Force stdin decoding with this charset"
                             "stdin. E.G: modules import", default="")
    parser.add_argument("--stdout-charset", nargs='?',
                        help="Force stdout encoding with this charset"
                             "stdin. E.G: modules import", default="")

    args = parser.parse_args()

    in_encoding = args.stdin_charset or sys.stdin.encoding or 'utf8'
    out_encoding = args.stdout_charset or sys.stdout.encoding or 'utf8'

    if args.version:
        print 'Pyped', __VERSION__
        sys.exit(0)

    if args.b:
        exec args.b in locals()

    try:

        command = args.expression.decode(in_encoding)
        if args.i:

            x = (l.decode(in_encoding).strip() for l in sys.stdin)
            try:
                exec "iterable = iter(%s)" % command in locals()
            except TypeError:
                print "\n /!\ Make sure your expression can be safely passed to iter()"
                print "===============================================================\n"
                raise

            for item in iterable:
                print unicode(item).encode(out_encoding)

        else:
            for i, x in enumerate(sys.stdin):
                x = x.decode(in_encoding).strip()
                exec u"print unicode((%s)).encode('%s')" % (command, out_encoding) in locals()

    except SyntaxError:
        if "print" in args.expression:
            sys.exit("You should not print into the Python expression: "
                     "each element will be printed automatically")
        if args.i:
            print "\n /!\ Make sure your expression can be safely passed to iter()"
            print "===============================================================\n"
        raise


if __name__ == '__main__':
    main()