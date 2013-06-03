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

import re
import os
import logging

#
# Command line options
#
parser=ArgumentParser(description='Git Tag Cleaner, a tool for removing old tags')

verbosity = parser.add_mutually_exclusive_group()
verbosity.add_argument('-v', '--verbose', action='count')
verbosity.add_argument('-q', '--quiet', action="store_true", help="be very quiet on stdout")

parser.add_argument('-o', '--output', dest="output",default="git-tag-cleaner.log",  help="log file output")
parser.add_argument('-g', '--git', dest="git", default=None, help="path to git repo (else uses GIT_DIR or cwd)")
parser.add_argument('-t', '--type', dest="type", default="commit", choices=['commit', 'all'], help="select the tag type")
parser.add_argument('-p', '--preserve', dest="preserve", default=None, help="regex of tags to save")
parser.add_argument('-d', '--delete', dest="delete", default=None, choices=['size', 'no-branch'], help="deletion criteria")
parser.add_argument('-r', '--remotes', dest="remotes", default=None, help="push tag deletions to remote (dangerous)")

# Logging
logger = logging.getLogger("git-tag-cleaner")

# A possibly excessive function to setup logging to file and stdout 
def setup_logging(quiet, verbose, out_file):
    # setup logging
    logger.setLevel(logging.DEBUG)
    lfmt = logging.Formatter('%(asctime)s:%(levelname)s - %(name)s - %(message)s')

    if verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    # output to stdout
    if not quiet:
        output = logging.StreamHandler()
        output.setLevel(log_level)
        output.setFormatter(lfmt)
        logger.addHandler(output)

    # output to file
    file_log = logging.FileHandler(out_file)
    file_log.setFormatter(lfmt)
    logger.addHandler(file_log)
    

def get_branches(repo_path, sha1):
    cmd = "git branch -r --contains %s" % (sha1)
    out = check_output(cmd, shell=True, stderr=STDOUT)
    logger.debug("cmd %s got %s" % (cmd, out))
    if (len(out)==0):
        return []
    else:
        branches = out.split("\n")
        return branches

if __name__ == "__main__":
    args = parser.parse_args()
    setup_logging(args.quiet, args.verbose, args.output)
    
    if not args.git:
        if os.environ.has_key('GIT_DIR'):
            args.git = os.environ['GIT_DIR']
        else:
            os.getcwd()
    repo = Repo(args.git)
    logger.info("using repo=%s" % (repo))
    skipped_tags = 0
    interesting_tags = []
    for t in repo.tags:
        logger.debug("Checking tag %s (points to %s)" % (t.name, t.tag))
        if args.type=="all" or not t.tag:
            interesting_tags.append(t)
        else:
            skipped_tags += 1

    logger.info("Created a list of %d tags (%d skipped)" % (len(interesting_tags), skipped_tags))
    # Filter out any tags we don't want touched
    if args.preserve:
        regex = re.compile(args.preserve)
        interesting_tags = [t for t in interesting_tags if not regex.match(t.name)]

            
    # sort the list based on size, largest fist
    logger.info("Sorting %d tags (skipped %d)" % (len(interesting_tags), skipped_tags))
    interesting_tags.sort(key=lambda tag: tag.object.size, reverse=True)

    # now go through the objects, identifying what we can delete
    for t in interesting_tags:
        hexsha = t.object.hexsha
        branches = get_branches(args.git, hexsha)
        if (len(branches)==0):
            logger.info("tag %s (size = %d) doesn't exist in any branches" % (t.name, t.object.size))
            if args.delete == "no-branch":
                logger.warning("deleting tag %s/%s from local repo" % (t.name, hexsha))
                repo.delete_tag(t)
            

