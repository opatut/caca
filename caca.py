#!/usr/bin/env python3
# encoding: utf-8

import argparse
import shutil
import os
import tempfile
import subprocess

DESCRIPTION = """caca - Copy And Convert Audio.

A very simple one-shot parallel audio converter that behaves a lot like cp"""

args = None

def detect_utils():
    tools = ['flac', 'lame', 'oggenc']
    for tool in tools:
        if not shutil.which(tool):
            raise FileNotFoundError("'{}' was not found on your system but is required".format(tool))

import flac, mp3
format_modules = [flac, mp3]

def get_extension(filename):
    ext = os.path.splitext(filename)[1].lower()
    if ext: ext = ext[1:] # cut away the '.'
    return ext

def first(fn, seq):
    for i in seq:
        if fn(i):
            return i
    return None

def shell_command(cmd, src, target):
    cmd = cmd.format(src=src.replace('"', '\\"'), target=target.replace('"', '\\"'))
    if args.verbose:
        print("--> " + cmd)
    return subprocess.call(cmd, shell=True) == 0

def convert(src, target):
    src_ext = get_extension(src)
    src_format = first(lambda module: src_ext in module.extensions, format_modules)

    target_ext = get_extension(target)
    target_format = first(lambda module: target_ext in module.extensions, format_modules)

    if not src_format or not target_format:
        return False

    if src_ext == target_ext:
        return copy_raw(src, target)

    # check whether we can convert directly between those formats
    direct = src_format.direct_convert(target_ext, src, target)
    if direct:
        return shell_command(direct, src, target)

    def composed():
        with tempfile.NamedTemporaryFile() as f:
            return shell_command(src_format.decode, f.name, target) and \
                shell_command(target_format.encode, f.name, target)

    return composed


def copy_raw(src, target):
    shutil.copyfile(src, target)
    return True


def handle_file(src, target):
    ext = get_extension(src)

    # create target directory
    target_dir = target if os.path.isdir(target) else os.path.dirname(target)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # build target filename
    f, e  = os.path.splitext(os.path.basename(src))
    target = os.path.join(target_dir, f + "." + args.format)

    if os.path.exists(target) and args.skip_existing:
        if args.verbose:
            print("[existing] '{}' -> '{}'".format(src, target))
        return

    if convert(src, target):
        if args.verbose:
            print("[converted] '{}' -> '{}'".format(src, target))

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
    parser.add_argument("-S", "--skip-existing", help="do not overwrite existing files", action="store_true")
    parser.add_argument("-f", "--format", help="target file extension (mp3/flac/ogg/wav)", default="mp3")

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
