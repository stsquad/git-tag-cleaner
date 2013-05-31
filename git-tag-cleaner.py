#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Git Tag Cleaner
# Copyright (C) 2013 Alex Bennée <alex@bennee.com>
# License: GPLv3
#
# A utility script for cleaning old tags that reference very large
# commits from a git repository.
#

from argparse import ArgumentParser

#
# Command line options
#
parser=ArgumentParser(description='Git Tag Cleaner, a tool for removing old tags')
parser.add_argument('-v', '--verbose', dest="verbose", action='count')
parser.add_argument('-g', '--git', dest="git", default=None, description="path to git repo (else uses cwd)")
parser.add_argument('-d', '--delete', dest="delete", default=None, description="deletion criteria (size, no-branch)")
parser.add_argument('-r', '--remotes', dest="remotes", default=None, description="push tag deletions to remote (dangerous)")

if __name__ == "__main__":
    args = parser.parse_args()


