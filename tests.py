# -*- coding: utf-8 -*-

from __future__ import (unicode_literals, print_function)

import os
import sys
import shlex
import tempfile
import subprocess

from io import BytesIO

try:
    import pytest
except ImportError:
    sys.exit("The unit tests require the package 'pytest' to be installed.")

import six

from pyped import execute_statements, __VERSION__



@pytest.fixture
def assert_print(capfd):
    """ Return a function that check expected strings have been printed """
    def _(*expected):
        """ Check was expected strings have been printed """
        expected = "\n".join(expected)

        if not expected.endswith("\n"):
            expected += "\n"

        resout, reserr = capfd.readouterr()
        assert resout == expected

    return _

@pytest.fixture
def assert_cmd_print():
    """ Return a function that check a command printed expected strings"""
    def _(cmd_args, expected_strings, stdin=None):
        """ Check a command printed expected strings """

        if isinstance(cmd_args, six.binary_type):
            cmd_args = [cmd_args]

        cmd = [sys.executable.encode('ascii'), b"pyped.py"]

        cmd.extend(cmd_args)

        if six.PY3:
            cmd = [x.decode('utf8') for x in cmd]

        if not isinstance(expected_strings, six.binary_type):
            expected_strings = b"\n".join(expected_strings)

        if not expected_strings.endswith(b"\n"):
            expected_strings += b"\n"

        try:

            if stdin is not None:
                if not isinstance(stdin, six.binary_type):
                    stdin = b"\n".join(stdin)

                if not stdin.endswith(b"\n"):
                    stdin += b"\n"

                # using a temporary file as pipe since real pipes cause
                # trouble with line breaks
                fake_pipe = tempfile.TemporaryFile()
                fake_pipe.write(stdin)
                fake_pipe.seek(0)
                # piped_stdin = subprocess.Popen(['echo', stdin], stdout=subprocess.PIPE, shell=True)
                # piped_stdin = subprocess.Popen(['echo', stdin], stdout=subprocess.PIPE, shell=True, universal_newlines=True)
                res = subprocess.check_output(cmd, stdin=fake_pipe,
                                              # stderr=subprocess.PIPE,
                                              universal_newlines=True)

            else:
                res = subprocess.check_output(cmd, stderr=subprocess.PIPE,  universal_newlines=True)
        except subprocess.CalledProcessError as e:
            print(e.output)
            raise

        if six.PY3:
            expected_strings = expected_strings.decode('utf8')

        assert res == expected_strings

    return _


def wrapper(statements, stdin=None, *args, **kwargs):
    """ A wrapper around pyped.execute_statements() to make testing easier.

        Convert scalar arguments in lists when required, and strings to
        file like objects if necessary.

        Add an empty list, named "lst", to the context so it can be filled
        with values
    """
    if isinstance(statements, six.binary_type):
        statements = [statements]

    if stdin:
        if not isinstance(stdin, six.binary_type):
            stdin = b"\n".join(stdin)
        stdin = BytesIO(stdin)

    return execute_statements(statements, stdin, *args, **kwargs)


# For non command tests, we use the OS separator in inputs, and the
# universal separator as ouput (since this is what print() add)


def test_execute_python_onliner(assert_print):
    wrapper(b"print(1)")
    assert_print("1")

def test_print_stdin_lines(assert_print):
    wrapper(b"print(x)", b"a")
    assert_print("a")
    wrapper(b"print(x)", [b"a", b"b"])
    assert_print("a", "b")
    # testing counter
    wrapper(b"print(i)", [b"a", b"b"])
    assert_print("1", "2")

def test_option_additional_context(assert_print):
    wrapper(b"print(foo)", b"1", additional_context={'foo': 'bar'})
    assert_print("bar")

def test_option_autoprint(assert_print):
    wrapper(b"1", autoprint=True)
    assert_print("1")
    wrapper(b"x", b"1", autoprint=True)
    assert_print("1")

def test_option_charset(assert_print):
    wrapper("print('é')".encode('cp1252'), stdin_charset="cp1252")
    assert_print("é")

    with pytest.raises(UnicodeDecodeError):
        wrapper("print('é')".encode('cp1252'))

def test_option_before(assert_print):
    wrapper(b"print(foo)", before=b"foo = 'bar'")
    assert_print("bar")

    with pytest.raises(NameError):
        wrapper(b"print(foo)")

def test_option_after(assert_print):
    wrapper(b"foo = 'bar'", after=b"print(foo)")
    assert_print("bar")

    with pytest.raises(NameError):
        wrapper(b"do = 'bar'", after=b"print(foo)")

def test_option_split(assert_print):
    wrapper(b"print('-'.join(f))", b"1\t2  3", split=b"\s+")
    assert_print("1-2-3")

def test_option_iterable(assert_print):
    wrapper(b"print(sum(map(int, l)))", [b"1", b"2"], iterable=True)
    assert_print("3")

    # split and iterable are not compatible
    with pytest.raises(ValueError):
        wrapper(b"print(sum(map(int, l)))", [b"1", b"2"],
                iterable=True, split="-")

def test_option_rstrip(capfd):
    execute_statements([b"print(x)"], BytesIO(b"1\n2\n"))
    resout, reserr = capfd.readouterr()
    assert resout == "1\n2\n"

    execute_statements([b"print(x)"], BytesIO(b"1\n2\n"),
                        rstrip="")
    resout, reserr = capfd.readouterr()
    assert resout == "1\n\n2\n\n"

    execute_statements([b"print(x)"],
                       BytesIO(b"1.\n2.\n"),
                       rstrip=".\n")
    resout, reserr = capfd.readouterr()
    assert resout == "1\n2\n"

def test_option_full(capfd):
    execute_statements([b"print(stdin)"], BytesIO(b"1\n2\n"),
                        full=True)
    resout, reserr = capfd.readouterr()
    assert resout == "1\n2\n\n"

    # x should not exists
    with pytest.raises(NameError):
        execute_statements([b"print(x)"], BytesIO(b"1\n2\n"),
                            full=True)

    # split should work
    execute_statements([b"print(f[0])"],
                        BytesIO(b"1-\n" + b"2\n"),
                        full=True, split=b"-")
    resout, reserr = capfd.readouterr()
    assert resout == "1\n"

    # rstrip should have no effect
    execute_statements([b"print(stdin)"], BytesIO(b"1\n2\n"),
                       full=True, rstrip=b"")
    resout, reserr = capfd.readouterr()
    assert resout == "1\n2\n\n"

    # you should not be able to set full and iterable together
    with pytest.raises(ValueError):
        execute_statements([b"print(x)"], BytesIO(b"1\n2\n"),
                           full=True, iterable=True)

    # decode works with full
    execute_statements([b"print(stdin)"], BytesIO("é".encode('cp1252')),
                       full=True, stdin_charset="cp1252")
    resout, reserr = capfd.readouterr()
    assert resout == "é\n"

    # autoprint works with full
    execute_statements([b"stdin"], BytesIO(b"1"), autoprint=True, full=True)
    resout, reserr = capfd.readouterr()
    assert resout == "1\n"


def test_option_json(assert_print, capfd):
    wrapper(b"print(j[0]['a'])", b'[{"a": 1}]', parse_json=True)
    assert_print("1")

    # x is not available
    with pytest.raises(NameError):
        wrapper(b"print(x)", b'[{"a": 1}]', parse_json=True)

    # you can't mix json parsing with iterable, full or split
    with pytest.raises(ValueError):
        wrapper(b"print(j[0]['a'])", b'[{"a": 1}]', parse_json=True, full=True)

    with pytest.raises(ValueError):
        wrapper(b"print(j[0]['a'])", b'[{"a": 1}]', parse_json=True, split="-")

    with pytest.raises(ValueError):
        wrapper(b"print(j[0]['a'])", b'[{"a": 1}]',
                parse_json=True, iterable=True)

    # works with charset
    wrapper(b"print(j[0]['a'])", '[{"a": "é"}]'.encode('cp1252'),
            parse_json=True, stdin_charset='cp1252')
    assert_print("é")

    # works with autoprint
    wrapper(b"j[0]['a']", b'[{"a": "1"}]', parse_json=True, autoprint="True")
    assert_print("1")

    # rstrip should have no effect
    execute_statements([b"print(j[0]['a'])"], BytesIO(b'[{"a": 1}]'),
                       parse_json=True, rstrip="")
    resout, reserr = capfd.readouterr()
    assert resout == "1\n"

def test_option_quiet(capfd):
    with pytest.raises(ZeroDivisionError):
        wrapper(b"1/0")

    wrapper(b"1/0", quiet=True)
    resout, reserr = capfd.readouterr()
    assert resout == ""

def test_option_filter(assert_print):
    wrapper(b"not int(x) % 2", [b"1", b"2", b"3", b"4"], filter_input=True)
    assert_print("2", "4")

    # works with decode
    data = ["é".encode('cp1252'), "è".encode('cp1252'),
            "é".encode('cp1252'), "è".encode('cp1252')]
    wrapper("x == 'é'".encode('cp1252'), data, filter_input=True,
            stdin_charset='cp1252')
    assert_print("é", "é")

    # works with split
    wrapper(b"not int(f[0]) % 2", [b"1,1", b"2,2", b"3,3", b"4,4"],
            split=b',', filter_input=True)
    assert_print("2,2", "4,4")

    # works with rstrip
    wrapper(b"not int(x) % 2", [b"1.", b"2.", b"3.", b"4."],
            filter_input=True, rstrip=".\n")
    assert_print("2", "4")

    # quiet makes it skip lines
    with pytest.raises(ZeroDivisionError):
        wrapper(b"1 / int(x)", [b"0", b"1", b"2", b"3"], filter_input=True)

    wrapper(b"1 / int(x)", [b"0", b"1", b"2", b"3"], filter_input=True, quiet=True)
    assert_print("1", "2", "3")


def test_command_version(assert_cmd_print):
    assert_cmd_print(b"--version", b"Pyped " + __VERSION__.encode('ascii'))

def test_command_one_liner(assert_cmd_print):
    assert_cmd_print(b"print(1)", b"1" )

def test_command_stdin_lines(assert_cmd_print):
    # iterate on lines
    assert_cmd_print(b"print(x)", [b"1"], stdin=[b"1"])
    assert_cmd_print(b"print(x)", [b"a", b"b"], stdin=[b"a", b"b"])

    # testing counter
    assert_cmd_print(b"print(i)", [b"1", b"2"], stdin=[b"a", b"b"])

def test_command_autoprint(assert_cmd_print):
    assert_cmd_print([b"1", b"-p"], b"1")
    assert_cmd_print([b"x", b"-p"], [b"a", b"b"], stdin=[b"a", b"b"])

def test_command_before(assert_cmd_print):
    assert_cmd_print([b'print(foo)', b'-b', b"foo = 'bar'"], b"bar")

def test_command_after(assert_cmd_print):
    assert_cmd_print([b'foo = "bar"', b'-a', b"print(foo)"], b"bar")

def test_command_split(assert_cmd_print):
    assert_cmd_print([ b"print('-'.join(f))", b"-s", b"\s+"],
                     b"1-2-3", b"1\t2  3")

def test_command_iterable(assert_cmd_print):
    assert_cmd_print([b"print(sum(map(int, l)))", b"-i"], b"3", [b"1", b"2"])

def test_command_rstrip(assert_cmd_print):
    assert_cmd_print([b"print(x)", b"--rstrip=''"],
                     [b"1", b"",  b"2", b"\n"], [b"1", b"2"])

def test_command_full(assert_cmd_print):
    assert_cmd_print([b"print(stdin)", b"--full"],
                     b"1\n2\n\n", b"1\n" + b"2")

def test_command_json(assert_cmd_print):
    assert_cmd_print([b"print(j[0]['a'])", b"--json"],  b"1", b'[{"a": 1}]')

def test_command_quiet():
    res = subprocess.check_output([sys.executable, "pyped.py", "1/0", "-q"])
    assert not res

def test_command_filter(assert_cmd_print):
    assert_cmd_print([b"not int(x) % 2", b'-f'],
                     [b"2", b"4"], [b"1", b"2", b"3", b"4"])

def test_command_error(capfd):
    res = subprocess.Popen([sys.executable, "pyped.py", "1/0"],
                           stderr=subprocess.PIPE)
    if not six.PY3:
        assert res.stderr.read().strip() == "ZeroDivisionError: integer division or modulo by zero"
    else:
        assert res.stderr.read().strip() == b"ZeroDivisionError: division by zero"

# I can't find a way to reliably test encoding on Python 2/3 and Linux/Windows
# so this will have to wait.

# def test_command_charset(assert_cmd_print):

#     cmd = [sys.executable, "pyped.py", 'print(x.encode("cp1252"))',
#            "--stdin-charset", "cp1252"]

#     if not six.PY3:
#         cmd = [sys.executable, "pyped.py", 'print(x.encode("cp1252"))',
#                "--stdin-charset", "cp1252"]
#         cmd = [x.encode('cp1252') for x in cmd]
#     else:
#         cmd = [sys.executable, "pyped.py", 'print(x)',
#            "--stdin-charset", "cp1252"]

#     # using a temporary file as pipe since real pipes cause
#     # trouble with line breaks
#     fake_pipe = tempfile.TemporaryFile()
#     fake_pipe.write("é".encode('cp1252'))
#     fake_pipe.seek(0)
#     res = subprocess.check_output(cmd, stdin=fake_pipe, universal_newlines=True)

#     if not six.PY3:
#         assert res == "é\n".encode("cp1252")
#     else:
#         assert res == "é\n"
