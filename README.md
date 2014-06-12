Pyped: command that pipes data from bash to Python, and vice-versa
=================================================================

*WARNING: since the last version the command line name "py" has been
renamed to "pyp" to avoid conflict with the new tool in the Python
stdlib named "py". It means pyped is now incompatible with the
"Python Power at the Prompt" project sharing the same name and goals.*

Pyped is a command-line tool that let you process another command
output with a Python one-liner like Perl or AWK.

Ever wish you could do this::

    $ ps aux | pyp "line = x.split()" "print(line[1], line[-1])" | grep worker
    18921 [kworker/1:2]
    22489 [kworker/3:0]
    24065 [kworker/3:3]
    24869 [kworker/u:3]
    25463 [kworker/u:1]
    25511 [kworker/2:2]
    25720 [kworker/0:2]
    26343 [kworker/0:1]
    26491 [kworker/2:0]
    26569 [kworker/1:0]
    26592 [kworker/u:0]
    26861 worker

Or this::

    $ ls -1 | pyp -i "for x in Counter(path(x.split()[-1]).ext for x in l).items(): print(x)"
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

It works with Python 2.7 and 3.4, although it uses __future__ imports to
enforce a lot of 3.X stuff such as unicode literals and the print() function.

How to use ?
=============

Usage::

    $ pyp "any python one-liner"
    $ shell_command | pyp [options] "any python one-liner" [another python one-liner] [| another_shell_function]

In the second example, you pipe data to pyped. In that case, you python code
will have access to the variable `x`, which will be a line from
stdin converted to unicode (with no ending '\n'). Each line from stdin
will be stuffed to `x` one by one, and your python code
will be executed for each new value for `x`

You'll also have access to the variable `i`, an integer incremented at each
call of you Python statement, starting from 0.

Your code MUST print something, if you wish something to appear.

Without Pyped::

    $ echo "test"
    test
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

    $ pyp "print('test')"
    test
    $ ls /etc/ | tail -n 4 | pyp "print('%s %s' % (i, x.upper()))"
    0 WPA_SUPPLICANT
    1 X11
    2 XDG
    3 XML

You can even make long one time scripts::

    $ ps aux | pyp "
    if i > 0:
        values = x.split()
        user, pid = values[:2]
        command = ' '.join(values[10:])
        if user != 'root':
            print('\"%s\";\"%s\";\"%s\"' % (user.upper(), pid, command))
    "
    "SYSLOG";"741";"rsyslogd -c5"
    "AVAHI";"788";"avahi-daemon: running"
    "AVAHI";"791";"avahi-daemon: chroot helper"
    "DAEMON";"1271";"atd"
    "WHOOPSIE";"1289";"whoopsie"
    "MYSQL";"1304";"/usr/sbin/mysqld"
    "ME";"1699";"ps aux"
    "ME";"2167";"-"
    "TIMIDITY";"2202";"/usr/bin/timidity -Os -iAD"
    "RTKIT";"2594";"/usr/lib/rtkit/rtkit-daemon"
    "ME";"2763";"/usr/bin/gnome-keyring-daemon --daemonize --login"
    "ME";"2774";"gnome-session --session=ubuntu"


Options
=======

-i
***

If you pass `-i`, then `x` will not exists, but `l` will contain
an iterable for which each call to `next()` return a line of stdin,
converted to unicode.

It is mainly used for processing you wish to apply to the whole stdin such as joining or for global counters.

E.G::

    $ ls /etc/ | tail -n 4 | pyp -i "print('-'.join(i.strip() for i in l))"
    wpa_supplicant-X11-xdg-xml

-p
***

Automatically print the result of your Python expression.

E.G::

    $ ls /etc/ | tail -n 4 | pyp -p 'x.upper()'
    WPA_SUPPLICANT
    X11
    XDG
    XML

WARNING : other flags usually accept Python **statement** (if, for, etc).  If
you use this flag, most of them will now only accect **expressions**
(stuff you can pass directly to the print function).

-f
***

Filter stdin using a Python expression (like grep, but on any python condition).

E.G::

    $ cat /etc/fstab | pyp -f 'len(x) < 45 and "/" in x'
    # / was on /dev/sda7 during installation
    # swap was on /dev/sda6 during installation

WARNING : other flags accept Python **statement** (if, for, etc). This flags
only accept **expressions** (stuff you can pass directly a if keyword).

-b
***

Pass a statement you wish to run BEFORE reading from stdin.
Mainly used for imports.

E.G::

    $ ls /etc/ | tail -n 4 | pyp "print(pickle.dumps(x))" -b "import pickle"
    Vwordpress
    p0
    .
    Vwpa_supplicant
    p0
    .
    VX11

This is executed only once.

-a
***

Pass a statement you wish to run AFTER reading all stdin.

Is is executed in a finally clause, so it runs even if your code fails before.

Mainly used for counters and cleanup.

E.G::

    $ ls /etc/ | tail -n 4 | pyp "x" -a 'print(i)'
    wpa_supplicant
    X11
    xdg
    xml
    3

This is executed only once.


--stdin-charset
*****************

Force the charset to decode input. Otherwise, we try to
detect it, and fallback on UTF-8 if it fails.

E.G::

    $ ls /etc/ | tail -n 4 | pyp "x.split('-')[0]" --stdin-charset ascii
    wpa_supplicant
    X11
    xdg
    xml

Be careful, that could fail miserably if you choose a bad charset:

    $ ls /etc/ | tail -n 4 | pyp "é" --stdin-charset ascii
    'ascii' codec can't decode byte 0xc3 in position 0: ordinal not in range(128)

--rstrip
************

Each line from stdin has .rstrip('\n') applied to it before being
passed to your code so you can call `print()` without thinking about it.

However, if you do wish to keep the line breaks, use --rstrip=''.

The usual result::

    $ ls /etc/ | pyp -i "for x in list(l)[:5]: print(x)"
    total 2,5M
    drwxr-xr-x 204 root    root     12K déc.   1 16:40 .
    drwxr-xr-x  26 root    root    4,0K nov.  12 07:37 ..
    drwxr-xr-x   3 root    root    4,0K mars   7  2013 acpi
    -rw-r--r--   1 root    root    3,0K avril 26  2011 adduser.conf

The result if you supress right stripping::

    $ ls /etc/ | pyp -i "for x in list(l)[:5]: print(x)" --rstrip=''
    total 2,5M

    drwxr-xr-x 204 root    root     12K déc.   1 16:40 .

    drwxr-xr-x  26 root    root    4,0K nov.  12 07:37 ..

    drwxr-xr-x   3 root    root    4,0K mars   7  2013 acpi

    -rw-r--r--   1 root    root    3,0K avril 26  2011 adduser.conf


--json
************

Parse stdin as JSON, and make the whole thing accessible in a "j" variable.

    $ echo '[{"foo": "bar"}]' | pyp -j "print(j[0]['foo'])"
    bar


Imports
==========

Before doing any processing, we import several modules so they are
immediatly available in your Python code::

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

    from itertools import *
    from uuid import uuid4
    from datetime import datetime, timedelta
    from collections import Counter, OrderedDict

We also import these 4 third party libraries::

    import arrow # better datetime
    import requests # better http request

    from minibelt import * # better itertools
    from path import path # better path handling

They should have been installed by setuptools automatically, so if you use pip or
easy_install, you are good to go.

If you didn't, and you don't have them installed, these imports will be ignored.

While Pyped is based on Python 2.7, it also imports some backported features
from Python 3::

    from __future__ import (unicode_literals, absolute_import,
                            print_function, division)

This means `print` is a function, any string is unicode by default and does
not need to be prefixed by `u`, division doesn't truncate and
imports are absolute (but you can use the relative import syntax).

This way, pyped run on Python 3.
