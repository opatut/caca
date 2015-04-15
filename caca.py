#!/usr/bin/env python3
# encoding: utf-8

import argparse
import shutil
import os
import shutil

DESCRIPTION = """caca - Copy And Convert Audio.

A very simple one-shot parallel audio converter that behaves a lot like cp"""

args = None

def detect_utils():
    tools = ['flac', 'lame', 'oggenc']
    for tool in tools:
        if not shutil.which(tool):
            raise FileNotFoundError("'{}' was not found on your system but is required".format(tool))


def convert_flac(src, target):
    pass

def copy_raw(src, target):
    shutil.copyfile(src, target)

def convert_ogg(src, target):
    pass

extensions = {
    'flac': convert_flac,
    'mp3': copy_raw,
    'ogg': convert_ogg
}

def handle_file(src, target):
    # get the file type by extension
    ext = os.path.splitext(src)[1].lower()
    if ext: ext = ext[1:] # cut away the '.'

    # create target directory
    target_dir = target if os.path.isdir(target) else os.path.dirname(target)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)


    if ext in extensions:
        if args.verbose:
            print("[convert] '{}' -> '{}'".format(src, target))

        extensions[ext](src, target)

    else:
        if args.skip_unknown:
            if args.verbose:
                print("[skip] '{}'".format(src))
        else:
            if args.verbose:
                print("[copy] '{}' -> '{}'".format(src, target))

            copy_raw(src, target)


def handle_path(src, target):
    if os.path.isdir(src):
        for entry in os.listdir(src):
            handle_path(os.path.join(src, entry), os.path.join(target, entry))
    else:
        handle_file(src, target)


def main():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("sources", metavar="SOURCE", nargs='+', help="input path")
    parser.add_argument("target", metavar="TARGET", help="output path")
    parser.add_argument("-v", "--verbose", help="print progress output", action="store_true")
    parser.add_argument("-R", "-r", "--recursive", help="copy directories recursively", action="store_true")
    parser.add_argument("-a", "--archive", help="same as --recursive but preserves attributes", action="store_true")
    parser.add_argument("-s", "--skip-unknown", help="do not copy unknown file types", action="store_true")

    # overwrite args array
    global args
    args = parser.parse_args()

    detect_utils()

    # Handle case where we have more than one sources but target is not a directory
    if len(args.sources) > 1 and os.path.isfile(args.target):
        raise RuntimeException("target '{}' is not a directory".format(args.target))

    # Handle case where the source is a directory but target is a file
    if os.path.isdir(args.sources[0]) and os.path.isfile(args.target):
        raise RuntimeException("cannot overwrite non-directory '{}' with directory '{}'".format(args.target, args.sources[0]))

    for src in args.sources:
        handle_path(src, args.target)

if __name__ == '__main__':
    main()
