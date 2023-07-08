#!/usr/bin/env python

import datetime
import dateutil.parser
import json
from pathlib import Path
import shutil


now = datetime.datetime.now(datetime.timezone.utc)
cutoff = now - datetime.timedelta(days = 90)


def stale(pull: Path) -> bool:
    info_path = pull / '_preview_data.json'

    try:
        with info_path.open('rt') as fp:
            info = json.load(fp)
    except json.JSONDecodeError:
        print(f"::error file={info_path.absolute}::Invalid build info for pull #{pull.name}")

    pr_time = dateutil.parser.isoparse(info['time'])

    return pr_time < cutoff


def cleanup(base: Path, deleted):
    for pull in base.iterdir():
        if pull.is_dir:
            if stale(pull):
                shutil.rmtree(pull)
                deleted(pull)


if __name__ == "__main__":
    from sys import argv
    from os import environ
    if len(argv) < 2:
        print(f"Not enough arguments! Usage: {argv[0]} <repo>")
        exit(1)
    
    dest = Path(argv[1]) / 'pull'
    if 'GITHUB_STEP_SUMMARY' in environ:
        with open(environ['GITHUB_STEP_SUMMARY'], 'at') as fp:
            fp.write("# Cleaned up previews\n\n")
            cleanup(dest, lambda path: fp.write(f'- `#{path.name}`\n'))
    else:
        cleanup(dest, lambda _: None)
    
