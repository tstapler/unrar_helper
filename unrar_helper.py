#!/usr/bin/env python
import fnmatch
import logging
import os
import re
import subprocess
import sys
from enum import Enum
from pathlib import Path
from typing import List

logging.basicConfig(stream=sys.stdout, format='%(message)s', level=logging.INFO)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Situation(str, Enum):
    COMPLETE = 'directory has already been successfully extracted'
    NEEDS_CLEANUP = 'directory has already been extracted but needs intermediate files cleaned up'
    NEEDS_UNRAR = 'directory needs to have files extracted'
    NO_RARS = 'directory has no rar files'


def needs_unrar(directory: Path) -> Situation:
    """Does this directory have a rar file but not video files"""
    rar_files = [f for f in directory.glob("*.rar")]
    rar_part_files = [f for f in directory.glob('*.r[0-9]*')]
    rar_files.extend(rar_part_files)

    if not rar_files:
        return Situation.NO_RARS

    rar_file_name = rar_files[0].stem

    movie_files = []
    for file_type in ['mkv', 'iso', 'avi', 'mp4']:
        movie_files.extend(case_insensitive_glob(directory, f'{rar_file_name}.{file_type}'))

    if rar_files and rar_part_files and movie_files and len(rar_files) != len(rar_part_files):
        return Situation.NEEDS_CLEANUP

    if rar_files and not movie_files:
        return Situation.NEEDS_UNRAR

    return Situation.COMPLETE


def case_insensitive_glob(path, pattern):
    list_path = [i for i in os.listdir(path) if os.path.isfile(os.path.join(path, i))]
    return [os.path.join(path, j) for j in list_path if re.match(fnmatch.translate(pattern), j, re.IGNORECASE)]


def main(target, dry_run=False):
    """Scan a directory for rarfiles that need to be unrar'd"""
    dirs_to_unrar = [
        d for d in Path(target).iterdir() if d.is_dir
    ]
    for directory in dirs_to_unrar:
        situation = needs_unrar(directory)

        if situation in [Situation.COMPLETE, Situation.NO_RARS]:
            logger.debug(f"Skipping {situation} {directory}")
            continue

        rar_files = [f for f in directory.glob('*.rar')]
        rar_part_files = [f for f in directory.glob('*.r[0-9]*')]
        rar_files.extend(rar_part_files)

        rar_name = rar_files[0].stem
        rar_file = Path(directory, f"{rar_name}.rar")
        rm_command = ['rm', str(rar_file)]
        if situation == Situation.NEEDS_UNRAR:
            logger.info(f"{situation} {directory}")
            unrar_command = [
                'unrar', 'e', '-o-',
                str(rar_file)
            ]
            run_commands_in_dir([unrar_command, rm_command], directory, dry_run=dry_run)
        elif situation == Situation.NEEDS_CLEANUP:
            logger.info(f"{situation} {directory}")
            if rar_part_files:
                run_commands_in_dir([rm_command], directory, dry_run=dry_run)
            else:
                logger.warning(f"Could not find part files in {directory} before cleanup, this should not happen")


def run_commands_in_dir(commands: List[List[str]], directory: Path, dry_run=False):
    for command in commands:
        if dry_run:
            logger.debug(" ".join(command))
        else:
            logger.info(" ".join(command))
            subprocess.run(command, cwd=directory)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="A helper for unraring completed torrents.")
    parser.add_argument(
        '--dir',
        dest="dir",
        help="The directory where your completed torrents are placed.")
    parser.add_argument('--dry-run', dest="dry", action="store_true")
    parser.add_argument('--debug', dest="debug", action="store_true")

    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)
    main(args.dir, args.dry)
