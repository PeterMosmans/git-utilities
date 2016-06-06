#!/usr/bin/env bash

# pull_upstream_changes - Updates repo and applies upstream changes
#
# Copyright (C) 2016 Peter Mosmans [Go Forward]
#                    <support AT go-forward.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.


# File which has to exist in the target directory to qualify as target
FINGERPRINT=""
# List of files and directories that need to be updated
SOURCEFILES=".git/hooks/pre-commit"
# Root directory within source repo
SOURCEROOT=""


## Don't change anything below this line
VERSION=0.3

source=$(dirname $(readlink -f $0))
target=$1

if [ -z "$target" ]; then
    target=$(readlink -f .)
    if [ "${target}" == "${source}" ]; then
        echo "Usage: pull_upstream_changes [TARGET]"
        echo "       or run from within target directory"
        exit
    fi
fi

# Check if the target actually contains the repository
if [ !-z ${FINGERPRINT} ] && [ ! -d $target/dtd ]; then
   echo "[-] ${target} does not contain the correct repository"
   exit
fi

# Update repository
echo "[*] Updating source repository (${source})..."
pushd "$source" >/dev/null && git pull && popd >/dev/null

# Only update newer files
echo "[*] Applying changes (if any)..."
for sourcefile in ${SOURCEFILES}; do
    if [ -d "${source}/${SOURCEROOT}/${sourcefile}" ]; then
       cp -vr ${source}/${SOURCEROOT}${sourcefile} $target/${sourcefile}
    else
        cp -v ${source}/${SOURCEROOT}${sourcefile} $target/${sourcefile}
    fi
done
echo "[+] Done"
