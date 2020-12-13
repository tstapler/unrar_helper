#!/usr/bin/env python
import asyncio
from pathlib import Path
import subprocess


def needs_unrar(directory: Path):
    """Does this directory have a rar file but not video files"""
    rar_files = [f for f in directory.glob('*.rar')]
    rar_files.extend([f for f in directory.glob('*.r[0-9]*')])
    movie_files = [f for f in directory.glob('*.mkv')]

    if rar_files and not movie_files:
        return True


def main(target, dry_run=False):
    """Scan a directory for rarfiles that need to be unrar'd"""
    dirs_to_unrar = [
        d for d in Path(target).iterdir() if d.is_dir and needs_unrar(d)
    ]
    for directory in dirs_to_unrar:
        rar_files = [f for f in directory.glob('*.rar')]
        rar_files.extend(f for f in directory.glob('*.r[0-9]*'))

        if rar_files:
            rar_name = rar_files[0].stem
            command = [
                'unrar', 'e', '-o-',
                str(Path(directory, f"{rar_name}.rar"))
            ]
            if dry_run:
                print(" ".join(command))
            else:
                subprocess.run(command, cwd=directory)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="A helper for unraring completed torrents.")
    parser.add_argument(
        '--dir',
        dest="dir",
        help="The directory where your completed corrents are placed.")
    parser.add_argument('--dry-run', dest="dry", action="store_true")

    args = parser.parse_args()
    main(args.dir, args.dry)
