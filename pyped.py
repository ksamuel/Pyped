#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

"""
Pyped is a command-line tool that let you process another
command output with a Python one-liner like Perl or AWK.

Like this:

    $ ps aux | py "'-'.join(x.split()[:3]) + '\n'" | grep 0.1

More informations: https://github.com/ksamuel/Pyped

"""


__VERSION__ = "0.3"


# we won't use all of these, they are imported to be available to
# the shell user

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
from datetime import date, time
now = datetime.datetime.now
today = datetime.datetime.today
from random import randint, randrange, choice
from collections import Counter, OrderedDict
from math import *


# we need a function to make a setup.py entry point
def main():


    parser = argparse.ArgumentParser(
                          description=__doc__,
                          formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("expression", help="The Python expression to evaluate",
                        nargs="?", default="x")
    parser.add_argument("-i", help="The x variable will be an iterable on the "
                                   "whole stdin.", action="store_true")
    parser.add_argument("-b", default="", nargs='?', metavar="expression",
                        help="Python expression to evaluate before reading "
                              "stdin. E.G: modules import")
    parser.add_argument("-a", default="", nargs='?', metavar="expression",
                        help="Python expression to evaluate after reading "
                              "stdin. THIS IS IN A FINALLY CLAUSE")
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

    # we need the import modules to be available as a context for future
    # exec, but they can't be included inside the function so we gather them
    # from globals
    context = globals()

    if args.version:
        print 'Pyped', __VERSION__
        sys.exit(0)

    try:

        command = args.expression.decode(in_encoding)

        # if x must be an iterable...
        if args.i:

            # we decode all the stdin content and add it to the
            # exec context
            context['x'] = (l.decode(in_encoding) for l in sys.stdin)

            if args.b:
                exec args.b in context

            try:
                # we exec the user expression and attemp to iter on
                # turn it into a generator
                # if it fails, we print it, else, we iterate and print
                # each element
                exec "x = (%s)" % command in context
                iterable = iter(context['x'])
            except TypeError:
                sys.stdout.write(unicode(context['x']).encode(out_encoding))
            else:
                for item in iterable:
                    sys.stdout.write(unicode(item).encode(out_encoding))

        # if x must be a string, we decode it and print it
        else:

            if args.b:
                exec args.b in context

            for i, x in enumerate(sys.stdin):
                context['x'] = x.decode(in_encoding)
                context['i'] = i
                exec "res = (%s)" % command in context
                if res is not None:
                    sys.stdout.write(unicode(res).encode(out_encoding))

    # 80 % of user errors come from them inserting prints
    except SyntaxError:
        if "print" in args.expression:
            sys.exit("You should not print into the Python expression: "
                     "just make sure you return an unicode string")

        raise

    finally:
        if args.a:
            exec args.a in context


if __name__ == '__main__':
    main()