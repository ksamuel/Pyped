Pyped: command that pipes data from bash to Python, and vice-versa
=================================================================

Pyped is a command-line tool that let you process another command output with a Python one-liner like Perl or AWK.

Ever wish you could do this::

    $ ps aux | py "'-'.join(x.split()[:3])" | grep 0.1
    user-2140-1.1
    user-2207-0.1
    root-5091-0.0
    user-20717-0.0
    user-20817-0.0

Or this::

    $ ls -1 | py -i "Counter([path.splitext(line)[1] for line in x]).items()"
    (u'.sh', 2)
    ('', 3)
    (u'.sh~', 3)
    (u'.py', 4)
    (u'.desktop', 1)


Pyped make that possible by giving you the `py` commande.

How to install ?
=================

Just type::

    pip install pyped

Please note this is beta code, it will void your waranty, you may take weight,
loose your job and your wife and endorse unspeakable believes.

How to use ?
=============

Usage::

    shell_command | py [options] "any python instructions" [| another_shell_function]

Your python code will have access to the variable `x`, which will be a line from
stdin converted to unicode. Each line from stdin will be stuffed to `x` one by
one `x`, and everytime your python code will be executed.

You'll also have access to the variable `i', an integer incremented at each
call of you Python expression, starting from 0.

Your code MUST return something convertible to unicode, as unicode() will be called on the result.

Without Pyped::

    $ ls /etc | tail
    wordpress
    wpa_supplicant
    X11
    xdg
    xml
    xul-ext
    xulrunner-1.9.2
    y-ppa-manager.conf
    zsh
    zsh_command_not_found

With Pyped::

    $ ls /etc/ | tail | py "str(i) + ' ' + x.upper()"
    0 WORDPRESS
    1 WPA_SUPPLICANT
    2 X11
    3 XDG
    4 XML
    5 XUL-EXT
    6 XULRUNNER-1.9.2
    7 Y-PPA-MANAGER.CONF
    8 ZSH
    9 ZSH_COMMAND_NOT_FOUND

Options
=======

-i
**

If you pass `-i`, then `x` will not contain a string, but an iterable for which
each call to `next()` return a line of stdin, converted to unicode.

It is mainly used for processing that you want to apply to the whole stdin.

If you use this option, your expression should result in an iterable for which
each call to `next()` return an object convertible to unicode, as unicode
will be called on it.

E.G::

    $ ls /etc/ | tail | ./pyped.py -i "['-'.join(i.strip() for i in x)]"
    wordpress-wpa_supplicant-X11-xdg-xml-xul-ext-xulrunner-1.9.2-y-ppa-manager.conf-zsh-zsh_command_not_found

If you don't return an iterable, it will be printed as is.

-b
**

Pass an expression you wish to run before reading from stdin.
Mainly used for imports.

E.G::

    $ ls /etc/ | tail | py "pickle.dumps(x)" -b "import pickle"
    Vwordpress
    p0
    .
    Vwpa_supplicant
    p0
    .
    VX11


Note that before doing any processing, we import several modules so they are
immidiatly available in your Python code::

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

You can't set variables in that code.

-a
**

Pass an expression you wish to run after reading from stdin.

Is is executed in a finally clause, so it runs even if your code fails before.

Mainly used for counters and cleanup.

E.G::

    $ ls /etc/ | tail | ./pyped.py "x" -a 'print i'
    wordpress
    wpa_supplicant
    X11
    xdg
    xml
    xul-ext
    xulrunner-1.9.2
    y-ppa-manager.conf
    zsh
    zsh_command_not_found
    9


--stdin-charset and --stdout-charset
************************************

Force the charset to decode input, and encode output. Otherwise, we try to
detect it, and fallback on UTF-8 if it fails.

E.G::

    $ ls /etc/ | tail | py "x.split('-')[0]" --stdin-charset ascii
    wordpress
    wpa_supplicant
    X11
    xdg
    xml
    xul
    xulrunner
    y
    zsh
    zsh_command_not_found

Be careful, that could fail miserably if you choose a bad charset:

    $ ls /etc/ | tail | py "é" --stdout-charset ascii
    Traceback (most recent call last):
      File "py", line 67, in <module>
        exec u"print unicode((%s)).encode('%s')" % (command, out_encoding)
      File "<string>", line 1
        print unicode((é)).encode('ascii')
                       ^
    SyntaxError: invalid syntax

Some advices
=============

Do NOT print. Each element will be printed automatically.

Carreful with " and ', as you are dealing with bash and Python at the same time.

When doing a split(), you remove the line break. You may want to explicitly add it back.

If you don't want to print a line, just return None instead of a unicode string: it will be skipped.

