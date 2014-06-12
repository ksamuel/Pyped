#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        print_function, division)

"""
Pyped is a command-line tool that let you process another
command output with a Python one-liner like Perl or AWK.

Like this:

    $ ps aux | pyp "line = x.split()" "print(line[1], line[-1])" | grep worker

'x' being the content of each stdin line.

More informations: https://github.com/ksamuel/Pyped

"""


__VERSION__ = "1.2"


# we won't use all of these, they are imported to be available to
# the shell user

import sys
import os
import re
import json
import base64
import calendar
import csv
import itertools
import random
import hashlib
import tempfile
import argparse
import random
import math
import stat

from itertools import *
from uuid import uuid4
from datetime import datetime, timedelta
from collections import Counter, OrderedDict

try:
    import arrow
except ImportError:
    pass

try:
    import requests
except ImportError:
    pass

try:
    from minibelt import *
except ImportError:
    pass

try:
    from path import path
except ImportError:
    pass


# we need a function to make a setup.py entry point
def main():


    parser = argparse.ArgumentParser(
                          description=__doc__,
                          formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("expressions", help="The Python statement to evaluate",
                        nargs="+", default="print(x)")

    parser.add_argument("-i", help="An 'l' variable will be an iterable on the "
                                   "whole stdin. You'll have to iterate "
                                   "manually", action="store_true")

    parser.add_argument("-b", default="", nargs='?', metavar="expression",
                        help="Python statement to evaluate before reading "
                              "stdin. E.G: modules import")

    parser.add_argument("-a", default="", nargs='?', metavar="expression",
                        help="Python statement to evaluate after reading "
                              "stdin. THIS IS IN A FINALLY CLAUSE")

    parser.add_argument("-f", action="store_true",
                        help="Filter stdin according to the result of expression."
                              " If expression is True, the line is printed.")

    parser.add_argument("-p", action="store_true",
                        help="Automatically print the result of each expression.")

    parser.add_argument("-v", '--version', action="store_true",
                        help="Display the script version and quit")

    parser.add_argument("--json", action="store_true",
                        help="Parse stdin as JSON and pass the result as 'j'")

    parser.add_argument("--stdin-charset", nargs='?', default="",
                        help="Force stdin decoding with this charset")

    parser.add_argument("--rstrip", nargs='?', default="\n",
                        help="A character to strip from the right of the line.")

    args = parser.parse_args()

    in_encoding = args.stdin_charset or sys.stdin.encoding or 'utf8'

    # we need the import modules to be available as a context for future
    # exec, but they can't be included inside the function so we gather them
    # from globals
    context = globals()

    def execute_all(context):
        """ Execute all python statements/expressions in the given context """
        for expression in args.expressions:
            command = expression.decode(in_encoding)
            # command is an expression you need to print
            if args.p:
                print(eval(command, context))
            # execute as is
            else:
                exec command in context

    if args.version:
        print('Pyped', __VERSION__)
        sys.exit(0)

    try:
        if args.b:
            exec args.b.decode(in_encoding) in context

        # if stdin must be passed as an iterable
        if args.i:
            # we decode all the stdin content and add it to the
            # exec context
            context['l'] = (l.decode(in_encoding).rstrip(args.rstrip) for l in sys.stdin)
            execute_all(context)

        # if stdin must be filtered according to an expression
        elif args.f:
            # we decode all the stdin content, decode each line,
            # pass it as x, check if the result is True, and if yes
            # print it.
             for i, x in enumerate(sys.stdin):
                context['x'] = x.decode(in_encoding).rstrip(args.rstrip)
                context['i'] = i
                for expression in args.expressions:
                    if not eval(expression.decode(in_encoding), context):
                        break
                else:
                    print(context['x'])

        # stdin is json, just pass it as is
        elif args.json:
            context['j'] = json.loads(sys.stdin.read().decode(in_encoding))
            execute_all(context)

        else:
            # if stdin must be passed line by line
            mode = os.fstat(0).st_mode
            if stat.S_ISFIFO(mode) or stat.S_ISREG(mode):
                for i, x in enumerate(sys.stdin):
                    context['x'] = x.decode(in_encoding).rstrip(args.rstrip)
                    context['i'] = i
                    execute_all(context)

            # stdin is not redirected or piped : ignore it and just
            # execute the code
            else:
                execute_all(context)

    except Exception as e:
        sys.exit("%s: %s" % (e.__class__.__name__, e))

    finally:
        if args.a:
            exec args.a.decode(in_encoding) in context


if __name__ == '__main__':
    main()
