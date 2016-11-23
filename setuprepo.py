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
import sys
import subprocess
import tempfile
import textwrap


VERSION = '0.6'


def clone_repo(options):
    """
    Clones a repo using parameters in @options.
    """
    if options['no_clone']:
        return
    if os.path.isdir(os.path.join(options['target'], options['repo'])):
        print_error('Target directory already exists, not cloning')
        return
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
                                         options['repo'])], options)
    except IOError:
        print('no can do')
        result = False
    if not result:
        print_error('Failed cloning {0}/{1}/{2} to {3}'.
                    format(options['remote'], options['namespace'],
                           options['repo'], options['target']), -1)
    return result


def create_template(options):
    """
    Creates templatefile.
    """
    if not options['template'] or options['no_template']:
        return
    notes = os.path.join(options['notes'], options['repo'] + '.txt')
    if os.path.isfile(notes):
        print_error('Target notes file already exists, skipping template')
        return
    print_status('Creating notes file {0}/{1}.txt from {2}'.
                 format(options['notes'], options['repo'],
                        options['template']), options)
    try:
        result = execute_command(['cp', options['template'], notes], options)
        modify_file(notes, options, 'template')
        print_status('Created notes file file {0}'.format(notes))
    except IOError:
        print('no can do')
        result = False
    if not result:
        print_error('Failed creating template {0}/{1}.txt from {2}'.
                    format(options['notes'], options['repo'],
                           options['template']), -1)


def execute_command(cmd, options):
    """
    Executes command @cmd
    Shows output when @options['verbose'] is True

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
    if (result != 0) and options['verbose']:
        print_error(stderr)
    print_status(stdout, options)
    return result == 0


def modify_file(filename, options, filetype):
    """
    Modifies @filename inline with parameters in @options.
    @filetype is used to show which file is modified.
    """
    with open(filename, 'r') as inputfile:
        modified = modify_text(inputfile.read(), options, filetype)
    with open(filename, 'w') as outputfile:
        outputfile.write(modified)


def modify_text(textfile, options, filetype):
    """
    Modifies @textfile with parameters in @options.
    @filetype is used to show which file is modified.

    Returns modified @textfile.
    """
    if not options['no_modify']:
        print_status('Modifying {0}, replacing NAMESPACE with {1}, REMOTE with'
                     ' {2}, REPO with {3} and TARGET with {4}'.
                     format(filetype, options['namespace'], options['remote'],
                            options['repo'], options['target']), options)
        for keyword in ['namespace', 'remote', 'repo', 'target']:
            textfile = textfile.replace(keyword.upper(), options[keyword])
    return textfile


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
    parser.add_argument('-c', '--config', action='store',
                        help='load config file')
    parser.add_argument('-r', '--remote', type=str, action='store',
                        help="""remote repository address""")
    parser.add_argument('-n', '--namespace', type=str, action='store',
                        help="""namespace of the repository""")
    parser.add_argument('--no-clone', action='store_true',
                        help="""do not clone repository""")
    parser.add_argument('--no-modify', action='store_true',
                        help="""do not modify patch and/or template""")
    parser.add_argument('--no-patch', action='store_true',
                        help="""do not patch repository""")
    parser.add_argument('--no-template', action='store_true',
                        help="""do not create template""")
    parser.add_argument('--patchfile', type=str, action='store',
                        help="""patchfile for new repositories""")
    parser.add_argument('--prepare', action='store_true',
                        help="""clone the repo, create an original and
                        modified folder, and exit""")
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


def patch_repo(options):
    """
    Patches repository.
    """
    if not options['patchfile'] or options['no_patch']:
        return
    print_status('Patching {0}/{1} with {2}'.format(options['target'],
                                                    options['repo'],
                                                    options['patchfile']),
                 options)
    try:
        patchfile = os.path.join(options['target'],
                                 next(tempfile._get_candidate_names()))  # pylint: disable=protected-access
        execute_command(['cp', options['patchfile'], patchfile], options)
        modify_file(patchfile, options, 'patchfile')
        os.chdir(os.path.join(options['target'], options['repo']))
        result = execute_command(['patch', '-Np1', '-i', patchfile], options)
    except IOError:
        result = False
    finally:
        if os.path.isfile(patchfile):
            os.remove(patchfile)
    if not result:
        print_error('Failed patching {0}/{1} with {2}'.
                    format(options['target'], options['repo'],
                           options['patchfile']), options)


def preflight_checks(options):
    """
    Performs checks whether @options contain valid options.
    """
    if not options['target']:
        options['target'] = os.getcwd()
    if not options['template'] or not options['notes']:
        options['no_template'] = True
    if not options['patchfile']:
        options['no_patch'] = True
    if not options['no_clone']:
        for key in ['remote', 'target', 'namespace']:
            if key not in options or not options[key]:
                print_error('Missing parameter: {0}'.format(key), -1)
    try:
        if not os.path.isdir(options['target']):
            print_error('Target directory does not exist', -1)
        if not options['no_template'] and not \
           os.path.exists(options['template']):
            print_error('Template file does not exist', -1)
        if not options['no_patch'] and not \
           os.path.exists(options['patchfile']):
            print_error('Patchfile does not exist', -1)
    except TypeError:
        print_error('Error verifying paths', -1)


def prepare_patch(options):
    """
    Copy the cloned repository to an original and modified folder.
    """
    if options['prepare']:
        repo = os.path.join(options['target'], options['repo'])
        original = os.path.join(options['target'], 'original')
        modified = os.path.join(options['target'], 'modified')
        result = execute_command(['cp', '-r', repo, original], options) and \
            execute_command(['cp', '-r', repo, modified], options)
        if result:
            print_line('[+] Success: check {0} and {1}'.format(original,
                                                               modified))
            print_line("""[*] Hint for creating patchfiles:
            LC_ALL=C TZ=UTC diff -Nur original/ modified/ > patch.file""")
            sys.exit(0)
        else:
            print_error('Failed copying {0} to {1} and {2}'.format(repo,
                                                                   original,
                                                                   modified),
                        True)


def print_error(text, result=False):
    """
    Prints error message @text and exits with result code @result if not 0.
    """
    if len(text):
        print_line('[-] ' + text, True)
    if result:
        sys.exit(result)


def print_line(text, error=False):
    """
    Prints @text to stdout, or to stderr if @error is True.
    Flushes stdout and stdin.
    """
    if text:
        if not error:
            print(text)
        else:
            print(text, file=sys.stderr)
    sys.stdout.flush()
    sys.stderr.flush()


def print_status(text, verbose=False):
    """
    Prints status message @text if @verbose is True
    """
    if verbose and text:
        print_line('[*] ' + text)


def read_config(options):
    """
    Read parameters from @options['config'], but don't supersede non-empty
    @options parameters.

    Returns: an array of options.
    """
    filename = options['config']
    if not filename:
        return options
    try:
        with open(filename, 'r') as config_file:
            contents = config_file.read()
            for key in ['namespace', 'notes', 'patchfile', 'remote', 'target',
                        'template']:
                if not options[key]:
                    if contents and re.findall(r'(?:^|\n){0}:\s?(.*)'.format(key), contents):
                        options[key] = re.findall(r'(?:^|\n){0}:\s?(.*)'.format(key),
                                                  contents)[0]
                    if options[key] and options[key].lower() == 'false':
                        options[key] = False
    except IOError as exception:
        print_error('Could not open configuration file {0}: {1}'.
                    format(filename, exception.strerror), -1)
    except IndexError as exception:
        print_error('Missing variables in {0}'.format(filename), -1)
    return options


def main():
    """
    Main program loop.
    """
    banner = 'setuprepo.py version ' + VERSION
    options = read_config(parse_arguments(banner))
    preflight_checks(options)
    clone_repo(options)
    prepare_patch(options)
    patch_repo(options)
    create_template(options)


if __name__ == "__main__":
    main()
