#!/usr/bin/env python

"""
Sets up project structure (clone and configure repository)

Copyright (C) 2016 Peter Mosmans [Go Forward]
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from __future__ import absolute_import
from __future__ import print_function

import argparse
import os
import re
import string
import sys
import subprocess
import tempfile
import textwrap


VERSION = '0.2'
CONFIG_FILE = 'setuprepo.yml'


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


def print_status(text, options):
    """
    Prints status message @text if @options contains verbose.
    """
    if options['verbose']:
        print_line('[*] ' + text)


def parse_arguments(banner):
    """
    Parses command line arguments.
    Uses @banner when showing description.

    Returns: an array of options.
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(banner + '''\
 - Clones and configures (patches) a git repository

Copyright (C) 2016 Peter Mosmans [Go Forward]
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.'''))
    parser.add_argument('repo', type=str, help="""repository name""")
    parser.add_argument('--config', action='store', default=CONFIG_FILE,
                        help='Load config file (default {0})'.
                        format(CONFIG_FILE))
    parser.add_argument('--modify', action='store_true', default=False,
                        help='Modify patchfile before applying')
    parser.add_argument('-r', '--remote', type=str, action='store',
                        help="""remote repository address""")
    parser.add_argument('-n', '--namespace', type=str, action='store',
                        help="""namespace of the repository""")
    parser.add_argument('--patchfile', type=str, action='store',
                        help="""patchfile for new repositories""")
    parser.add_argument('-t', '--target', type=str, action='store',
                        help="""local target for the repository structure""")
    parser.add_argument('--notes', type=str, action='store',
                        help="""the directory where to create a notes file""")
    parser.add_argument('--template', type=str, action='store',
                        help="""an empty notes template""")
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='Be more verbose')
    options = vars(parser.parse_args())
    return options


def preflight_checks(options):
    """
    Performs checks whether @options contain valid options.
    """
    for key in ['remote', 'target', 'namespace']:
        if key not in options or not options[key]:
            print_error('Missing parameter: {0}'.format(key), -1)
    try:
        if not os.path.isdir(options['target']):
            print_error('Target directory does not exist', -1)
        if os.path.isdir(os.path.join(options['target'], options['repo'])):
            print_error('Target repository already exists', -1)
        if not os.path.exists(options['template']):
            print_error('Template file does not exist', -1)
        if not os.path.exists(options['patchfile']):
            print_error('Patchfile does not exist', -1)
    except TypeError:
        print_error('Error verifying paths', -1)


def read_config(options):
    """
    Reads parameters from @options['config'],  but doesn't overwrite non-empty
    @options parameters.

    Returns: an array of options.
    """
    filename = options['config']
    try:
        with open(filename, 'r') as config_file:
            contents = config_file.read()
            for key in ['namespace', 'notes', 'patchfile', 'remote', 'target',
                        'template']:
                if not options[key] and \
                   re.findall(r'{0}:\s?(.*)'.format(key), contents):
                    options[key] = re.findall(r'{0}:\s?(.*)'.format(key),
                                              contents)[0]
    except IOError as exception:
        print_error('Could not open configuration file {0}: {1}'.
                    format(filename, exception.strerror), -1)
    except IndexError as exception:
        print_error('Missing variables in {0}'.format(filename), -1)
    return options


def clone_repo(options):
    """
    Clones a repo using parameters in @options.
    """
    print_status('Cloning {0}/{1}/{2} to {3}'.format(options['remote'],
                                                     options['namespace'],
                                                     options['repo'],
                                                     options['target']),
                 options)
    try:
        os.chdir(options['target'])
        result = execute_command(['git', 'clone', '{0}/{1}/{2}'.
                                  format(options['remote'],
                                         options['namespace'],
                                         options['repo'])], options['verbose'])
    except IOError:
        print('no can do')
        result = False
    if not result:
        print_error('Failed cloning {0}/{1}/{2} to {3}'.
                    format(options['remote'], options['namespace'],
                           options['repo'], options['target']), -1)
    return result


def patch_repo(options):
    """
    Patches repository.
    """
    if not options['patchfile']:
        return
    print_status('Patching {0}/{1} with {2}'.format(options['target'],
                                                    options['repo'],
                                                    options['patchfile']),
                 options)
    try:
        temp_file = next(tempfile._get_candidate_names())  # pylint: disable=protected-access
        result = execute_command(['cp', options['patchfile'],
                                  temp_file], options['verbose'])
        if options['modify']:
            print_status('Modifying patchfile, replacing NAMESPACE with {0}, '
                         'REMOTE with {1}, REPO with {2} and '
                         'TARGET with {3}'.format(options['namespace'],
                                                  options['remote'],
                                                  options['repo'],
                                                  options['target']), options)
            with open(temp_file, 'w') as modify:
                with open(options['patchfile'], 'r') as patchfile:
                    for line in patchfile.read().splitlines():
                        for keyword in ['namespace', 'remote', 'repo',
                                        'target']:
                            line = string.replace(line, keyword.upper(),
                                                  options[keyword])
                        modify.write(line)
        else:
            result = execute_command(['cp', options['patchfile'],
                                      temp_file], options['verbose'])
        os.chdir(os.path.join(options['target'], options['repo']))
        result = execute_command(['patch', '-Np1', '-i', temp_file],
                                 options['verbose'])
    except IOError:
        result = False
    finally:
        os.remove(temp_file)
    if not result:
        print_error('Failed patching {0}/{1} with {2}'.
                    format(options['target'], options['repo'],
                           options['patchfile']), options)


def create_template(options):
    """
    Creates templatefile.
    """
    if not options['template']:
        return
    print_status('Creating template {0}/{1}.txt from {2}'.
                 format(options['notes'], options['repo'],
                        options['template']), options)
    try:
        result = execute_command(['cp', options['template'],
                                  os.path.join(options['notes'],
                                               options['repo'] + '.txt')],
                                 options['verbose'])
    except IOError:
        print('no can do')
        result = False
    if not result:
        print_error('Failed creating template {0}/{1}.txt from {2}'.
                    format(options['notes'], options['repo'],
                           options['template']), -1)


def main():
    """
    Main program loop.
    """
    banner = 'setuprepo.py version ' + VERSION
    options = read_config(parse_arguments(banner))
    preflight_checks(options)
    clone_repo(options)
    patch_repo(options)
    create_template(options)
    print_line('Success: check {0}/{1}'.format(options['target'],
                                               options['repo']))


if __name__ == "__main__":
    main()