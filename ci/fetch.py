#!/usr/bin/env python3
"""
Fetches updates for specified packages using `clydetools fetch`.
"""

import argparse
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from get_clyde import download_clyde, find_clyde_snapshot_url
from git import Repo
from utils import list_all_packages


def run_clydetools_fetch(package_files: list[Path]) -> None:
    with TemporaryDirectory() as temp_dir:
        clyde_dir = Path(temp_dir) / "clyde"
        clyde_url = find_clyde_snapshot_url()
        download_clyde(clyde_url, clyde_dir)

        package_files = [x.absolute() for x in package_files]
        subprocess.run(
            ["clydetools", "fetch", *package_files], check=True, cwd=temp_dir
        )


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter, description=__doc__
    )

    parser.add_argument("package_files", nargs="*")

    args = parser.parse_args()

    if args.package_files:
        package_paths = [Path(x) for x in args.package_files]
    else:
        repo = Repo(".")
        package_paths = list_all_packages(repo)

    run_clydetools_fetch(package_paths)

    return 0


if __name__ == "__main__":
    sys.exit(main())
# vi: ts=4 sw=4 et
