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


__VERSION__ = "1.4"


# we won't use all of these, they are imported to be available to
# the shell user

import sys
import os
import re
import json
import base64
import csv
import tempfile
import argparse
import random
import math
import stat
import itertools

from itertools import chain, cycle, islice, repeat, tee, groupby

from uuid import uuid4
from datetime import datetime, timedelta
from collections import Counter, OrderedDict
from hashlib import md5, sha1, sha256
from pprint import pprint

try:
    import arrow
except ImportError:
    pass

try:
    import requests
except ImportError:
    pass

try:
    from minibelt import (slugify, normalize, attr, dmerge, flatten,
                          get, iget, skip_duplicates, sset)
except ImportError:
    pass

try:
    from path import path
except ImportError:
    pass

# Python 3 compat
from six import exec_, PY3


if not PY3:
    from itertools import imap, izip, izip_longest

# we need a function to make a setup.py entry point and unit tests
def execute_statements(statements, stdin=None, additional_context=None,
                       quiet=False, iterable=False, autoprint=False,
                       filter_input=False, stdin_charset='utf8', before=None,
                       after=None, split=None, rstrip="\n", full=False,
                       parse_json=False):

    for options in itertools.combinations((full, parse_json, iterable), 2):
        if all(options):
            raise ValueError("You can only choose one of the following at the "
                             "same time : full stdin, stdin as iterable or "
                             "parse stdin as JSON.")

    if split and (parse_json or iterable):
        raise ValueError("You can't mix splitting stdin and parsing it as JSON "
                         "getting it as an iterable.")

    in_encoding = (getattr(stdin, 'encoding', None) or stdin_charset
                     or sys.stdin.encoding)
    if in_encoding in ('ascii', None, ''):
        in_encoding = 'utf8'

    context = additional_context or {}

    def execute_all(context):
        """ Execute all python statements/expressions in the given context """
        for statement in statements:
            try:
                statement = statement.decode(in_encoding)
            except AttributeError:
                pass # note a byte
            try:
                # command is an expression you need to print
                if autoprint:
                    res = eval(statement, context)
                    if res is not None:
                        print(res)
                # execute as is
                else:
                    exec_(statement, context)
            except Exception as e:
                if not quiet:
                    raise e

    try:
        if before:
            try:
                try:
                    before = before.decode(in_encoding)
                except AttributeError:
                    pass  # not bytes
                exec_(before, context)
            except Exception as e:
                if not quiet:
                    raise e
        if split:
            try:
                splitter = split.decode(in_encoding)
            except AttributeError:
                splitter = split # not bytes

        # if stdin must be passed as an iterable
        if iterable:
            # we decode all the stdin content and add it to the
            # exec context

            def _():
                for l in stdin:
                    try:
                        l = l.decode(in_encoding)
                    except AttributeError:
                        pass # note bytes
                    yield l.rstrip(rstrip)

            context['l'] = _()
            execute_all(context)

        elif full:
            # we decode all the stdin content and add it to the
            # exec context

            stdin = stdin.read()
            try:
                stdin = stdin.decode(in_encoding)
            except AttributeError:
                pass

            context['stdin'] = stdin
            if split:
                context['f'] = re.split(splitter,  context['stdin'])
            execute_all(context)

        # if stdin must be filtered according to an expression
        elif filter_input:
            # we decode all the stdin content, decode each line,
            # pass it as x, check if the result is True, and if yes
            # print it.
            for i, line in enumerate(stdin, 1):

                try:
                    line = line.decode(in_encoding)
                except AttributeError:
                    pass # note bytes
                line = line.rstrip(rstrip)

                if split:
                    context['f'] = re.split(splitter, line)

                context['x'] = line
                context['i'] = i
                for expression in statements:
                    try:
                        try:
                            expression = expression.decode(in_encoding)
                        except AttributeError:
                            pass # note a byte
                        if not eval(expression, context):
                            break
                    except Exception as e:
                        if not quiet:
                            raise e
                        break
                else:
                    print(context['x'])

        # stdin is json, just pass it as is
        elif parse_json:

            stdin = stdin.read()
            try:
                stdin = stdin.decode(in_encoding)
            except AttributeError:
                pass # not bytes

            context['j'] = json.loads(stdin)
            execute_all(context)

        else:
            # if stdin must be passed line by line
            if stdin:

                for i, line in enumerate(stdin, 1):

                    try:
                        line = line.decode(in_encoding)
                    except AttributeError:
                        pass # note bytes
                    line = line.rstrip(rstrip)

                    if split:
                        context['f'] = re.split(splitter, line)

                    context['x'] = line
                    context['i'] = i
                    execute_all(context)

            # stdin is not redirected or piped : ignore it and just
            # execute the code
            else:
                execute_all(context)

    finally:
        if after:
            try:
                try:
                    after = after.decode(in_encoding)
                except AttributeError:
                    pass  # not bytes
                exec_(after, context)
            except Exception as e:
                if not quiet:
                    raise e

def main():

    if "--version" in sys.argv:
        print('Pyped', __VERSION__)
        sys.exit(0)

    parser = argparse.ArgumentParser(
                          description=__doc__,
                          formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("statements", help="The Python statements to evaluate",
                        nargs="+")

    parser.add_argument("-i", help="An 'l' variable will be an Iterable on the "
                                   "whole stdin. You'll have to iterate "
                                   "manually", action="store_true")

    parser.add_argument("-b", default="", nargs='?', metavar="expression",
                        help="Python statement to evaluate Before reading "
                              "stdin. E.G: modules import")

    parser.add_argument("-a", default="", nargs='?', metavar="expression",
                        help="Python statement to evaluate After reading "
                              "stdin. THIS IS IN A FINALLY CLAUSE")

    parser.add_argument("-q", action="store_true",
                        help="Quietly ignore exception.")

    parser.add_argument("-f", action="store_true",
                        help="Filter stdin according to the result of expression."
                              " If expression is True, the line is printed.")

    parser.add_argument("-s", default="",   help="Split stdin, and pass it as "
                        "'f'. 'x' and 'i' or 'stdin' are still available.")

    parser.add_argument("-p", action="store_true",
                        help="Automatically Print the result of each expression.")

    parser.add_argument("-v", '--version', action="store_true",
                        help="Display the script Version and quit")

    parser.add_argument("--full", action="store_true",
                        help="Pass the full stdin content as 'stdin'")

    parser.add_argument("--json", action="store_true",
                        help="Parse stdin as JSON and pass the result as 'j'")

    parser.add_argument("--stdin-charset", nargs='?', default="",
                        help="Force stdin decoding with this charset")

    parser.add_argument("--rstrip", nargs='?', default="\n",
                        help="A character to strip from the right of the line.")

    args = parser.parse_args()

    # We need the imported modules to be available as a context for future
    # exec, but they can't be included inside the function so we gather them
    # from globals
    context = dict(globals())
    # Removing useless references
    for v in ('__VERSION__', '__builtins__', '__doc__', '__file__',
              '__name__', '__package__', 'argparse', 'division',
              'main', 'print_function', 'stat', 'unicode_literals',
              'absolute_import'):
        del context[v]

    try:

        # Check if data has been piped or redirected to stdin
        stdin = None
        mode = os.fstat(0).st_mode
        if stat.S_ISFIFO(mode) or stat.S_ISREG(mode):
            stdin = sys.stdin

        # this is where most of the work happen
        execute_statements(args.statements, stdin=stdin,
                           additional_context=context, quiet=args.q,
                           autoprint=args.p, stdin_charset=args.stdin_charset,
                           before=args.b, after=args.a, split=args.s,
                           iterable=args.i, rstrip=args.rstrip, full=args.full,
                           filter_input=args.f, parse_json=args.json)
    except Exception as e:
        if not args.q:
            sys.exit("%s: %s" % (e.__class__.__name__, e))


if __name__ == '__main__':
    main()