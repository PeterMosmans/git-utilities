#!/usr/bin/env python

"""
Updates (pulls) git repositories in bulk

Copyright (C) 2016 Peter Mosmans [Go Forward]
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from __future__ import absolute_import
from __future__ import print_function

import argparse
import glob
import os
import sys
import subprocess
import textwrap


VERSION = '0.2'


def execute_command(cmd, verbose=False):
    """
    Executes command @cmd
    Shows output when @quiet is False

    Returns: False if command failed
    """
    stderr = ''
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        result = process.returncode
    except OSError as exception:
        result = -1
        print_error('could not execute {0}'.format(cmd))
        print_error(format(exception.strerror))
    if (result != 0) and verbose:
        print_error(stderr)
    print_status(stdout, verbose)
    return result == 0


def print_line(text, error=False):
    """
    Prints @text to stdout, or to stderr if @error is True.
    Flushes stdout and stdin.
    """
    if not error:
        print(text)
    else:
        print(text, file=sys.stderr)
    sys.stdout.flush()
    sys.stderr.flush()


def print_error(text, result=False):
    """
    Prints error message @text and exits with result code @result if not 0.
    """
    if len(text):
        print_line('[-] ' + text, True)
    if result:
        sys.exit(result)


def print_status(text, verbose=False):
    """
    Prints status message @text if @verbose
    """
    if verbose and text:
        print_line('[*] ' + text)


def loop_repositories(options):
    """
    Finds all git repositories in @options['root'] and updates them.
    """
    for config in glob.glob(options['root'] + '*/.git/config'):
        repo = os.path.abspath(os.path.join(config, "../.."))
        print_status('Working on ' + repo)
        os.chdir(repo)
        if execute_command(['git', 'status'], options['verbose']):
            execute_command(['git', 'pull'], options['verbose'])


def parse_arguments(banner):
    """
    Parses command line arguments.
    Uses @banner when showing description.

    Returns: an array of options.
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(banner + '''\
 - Bulk updates git repositories

Copyright (C) 2016 Peter Mosmans [Go Forward]
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.'''))
    parser.add_argument('root', type=str, help="""root directory""")
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='Be more verbose')
    options = vars(parser.parse_args())
    return options


def preflight_checks(options):
    """
    Check whether valid @options are given.
    """
    try:
        if not os.path.isdir(options['root']):
            print_error('Root directory {0} does not exist'.
                        format(options['root']), -1)
    except TypeError:
        print_error('Error verifying paths', -1)


def main():
    """
    Main program loop.
    """
    banner = 'git-updater version ' + VERSION
    options = parse_arguments(banner)
    preflight_checks(options)
    loop_repositories(options)


if __name__ == "__main__":
    main()
