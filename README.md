# git-utilities
A collection of handy git hooks / scripts


## hooks

### hooks/pre-commit
This hook is for a local repository, and fires when committing to the repo. It validates files before they are committed.

There are currently three validators implemented: An XML validator, a YAML
validator and a Python validator.
The Python validator executes pylint, and you can specify a minimum pylint
score.

The XML validator needs the external `defusedxml` pip library, as that is a
safer alternative than the built-in `xml` library. Install `defusedxml` using

```
pip install -r requirements.txt
```

The configuration can be specified in the file `.git/hooks/pre-commit.yml`:
```
python: True
reject: True
treshold: 10
verbose: True
yaml: True
```

*python*: When set to True, validates all Python files using pylint. Pylint needs to be installed (`pip install pylint`
*reject*: When set to True, rejects the commit if validation fails.
*treshold*: When given a numerical value between 0 - 10, validates all Python files and fails if the pylint score is lower.
*verbose*: When set to True, shows status messages while committing.
*yaml*: When set to True, validates all Yaml files. The PyYAML library needs to be installed (`pip install pyyaml`

For easy installation, apply the `githooks.patch` file in your repository using
`patch -Np1 -i githooks.patch` in the root of your repository. This will install the githooks with default configuration values.

### hooks/pre-receive
This hook is for a hosted repository, and fires when people push commits to the repo. It validates files when they are received, and before they are updated.
You can set a variable  (`reject`) whether to reject the update when validation fails, or to allow the invalid file being updated. The default value is `True`, which means that updates will fail when validation fails.

There is currently one validator implemented in the `pre-receive` hook, the XML validator.

## install / configure / update repositories

### pull_upstream_changes.sh
A script to update a repo with upstream changes.
Sometimes you don't want to specify an upstream repository, but still want to pull and apply changes from an upstream source. This script allows you to specify which files can be safely updated by an upstream repo. It pulls the latest changes and applies them.
Can be run from within a target directory, or by specifying the target as parameter.

### setuprepo.py
A wrapper to execute one or multiple repetitive tasks:
+ Clones a repository to a local destination
+ Modifies the repository (e.g. adds githooks, changes the git configuration)
+ Modifies the repository based on given variables
+ Creates a new notes file from a given template
+ Modifies the notes fileile based on given variables

It can use configuration files, so you can use e.g. one for github and one for private repositories.
```
namespace: PeterMosmans
notes: /location/where/notes/should/be/stored
patchfile: /location/of/patch.file
remote: https://github.com
target: /where/repositories/are/cloned/to
template: /base/template.txt
```

```
usage: setuprepo.py [-h] [--config CONFIG] [-r REMOTE] [-n NAMESPACE]
                    [--no-clone] [--no-modify] [--no-patch] [--no-template]
                    [--patchfile PATCHFILE] [--prepare] [-t TARGET]
                    [--notes NOTES] [--template TEMPLATE] [-v]
                    repo

setuprepo.py version 0.5 - Clones and configures (patches) a git repository

Copyright (C) 2016 Peter Mosmans [Go Forward]
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

positional arguments:
  repo                  repository name

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG       load config file
  -r REMOTE, --remote REMOTE
                        remote repository address
  -n NAMESPACE, --namespace NAMESPACE
                        namespace of the repository
  --no-clone            do not clone repository
  --no-modify           do not modify patch and/or template
  --no-patch            do not patch repository
  --no-template         do not create template
  --patchfile PATCHFILE
                        patchfile for new repositories
  --prepare             clone the repo, create an original and modified
                        folder, and exit
  -t TARGET, --target TARGET
                        local target for the repository structure
  --notes NOTES         the directory where to create a notes file
  --template TEMPLATE   an empty notes template
  -v, --verbose         Be more verbose
```

All scripts are GPLv3 licensed.




