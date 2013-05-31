#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Git Tag Cleaner
# Copyright (C) 2013 Alex Bennée <alex@bennee.com>
# License: GPLv3
#
# A utility script for cleaning old tags that reference very large
# commits from a git repository. It uses the latest version of python-git (0.3)
# so may need extra packages installed.
#

from argparse import ArgumentParser
from git import Repo
from subprocess import check_output, STDOUT
import os

#
# Command line options
#
parser=ArgumentParser(description='Git Tag Cleaner, a tool for removing old tags')
parser.add_argument('-v', '--verbose', dest="verbose", action='count')
parser.add_argument('-g', '--git', dest="git", default=None, help="path to git repo (else uses GIT_DIR or cwd)")
parser.add_argument('-t', '--type', dest="type", default="commit", choices=['commit', 'all'], help="select the tag type")
parser.add_argument('-d', '--delete', dest="delete", default=None, choices=['size', 'no-branch'], help="deletion criteria")
parser.add_argument('-r', '--remotes', dest="remotes", default=None, help="push tag deletions to remote (dangerous)")


def get_branches(repo_path, sha1):
    cmd = "git branch -r --contains %s" % (sha1)
    out = check_output(cmd, shell=True, stderr=STDOUT)
    if (len(out)==0):
        return []
    else:
        branches = out.split("\n")
        return branches

if __name__ == "__main__":
    args = parser.parse_args()
    if not args.git:
        if os.environ.has_key('GIT_DIR'):
            args.git = os.environ['GIT_DIR']
        else:
            os.getcwd()
    repo = Repo(args.git)
    print "have repo=%s" % (repo)
    skipped_tags = 0
    interesting_tags = []
    for t in repo.tags:
        if args.type=="all" or not t.tag:
            interesting_tags.append(t)
        else:
            skipped_tags += 1

    print "Collected %d tags (skipped %d)" % (len(interesting_tags), skipped_tags)
    # sort the list based on size, largest fist
    interesting_tags.sort(key=lambda tag: tag.object.size, reverse=True)

    # now go through the objects, identifying what we can delete
    for t in interesting_tags:
        hexsha = t.object.hexsha
        branches = get_branches(args.git, hexsha)
        if (len(branches)==0):
            print "tag: %s (size = %d) doesn't exist in any branches" % (t.name, t.object.size)
            if args.delete == "no-branch":
                print "deleting tag"
                repo.delete_tag(t)
            

