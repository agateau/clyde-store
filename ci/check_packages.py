#!/usr/bin/env python3
"""
Check packages changed between TARGET and HEAD are valid.
"""
import argparse
import random
import subprocess
import sys
from pathlib import Path
from typing import Iterable

from get_clyde import (
    GITHUB_TOKEN,
    download_clyde,
    find_clyde_release_url,
    find_clyde_snapshot_url,
)
from git import Repo
from tui import eprint, progress
from utils import CLYDE_DIR, ROOT_DIR, is_package, list_all_packages, which

RANDOM_COUNT = 8

CI_DIRNAME = "ci"


def check_github_token() -> None:
    if not GITHUB_TOKEN:
        eprint(
            "CLYDE_GITHUB_TOKEN environment variable not set. Consider defining it"
            " to avoid being rate-limited."
        )


def iter_modified_files(repo: Repo, revision: str) -> Iterable[Path]:
    diff_index = repo.index.diff(revision)
    for diff in diff_index.iter_change_type("M"):
        assert diff.b_path
        yield Path(diff.b_path)
    for diff in diff_index.iter_change_type("A"):
        assert diff.b_path
        yield Path(diff.b_path)


def has_ci_changed(repo: Repo, paths: list[Path]) -> bool:
    return any(Path(CI_DIRNAME) in x.parents for x in paths)


def list_packages_to_check(
    repo: Repo, revision: str, *, random_count: int = RANDOM_COUNT
) -> list[Path]:
    progress("Listing packages to check")
    paths = list(iter_modified_files(repo, revision))
    packages = [x for x in paths if is_package(x)]
    if has_ci_changed(repo, paths):
        eprint(
            f"CI files have changed: adding a random selection of {random_count}"
            " packages"
        )
        all_packages = list_all_packages(repo)
        candidates = list(set(all_packages) - set(packages))
        if len(candidates) <= random_count:
            return all_packages
        packages.extend(random.sample(candidates, random_count))
    return packages


def check_packages(packages: list[Path]) -> None:
    # We must run the test in the current directory for now
    cmd = [which("clydetools"), "check"] + packages
    subprocess.run(cmd, cwd=ROOT_DIR)


def main() -> int:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter, description=__doc__
    )

    parser.add_argument("target")
    parser.add_argument("-a", "--all", action="store_true")
    parser.add_argument("-d", "--dry-run", action="store_true")
    parser.add_argument(
        "--rev",
        metavar="REVISION",
        help="Check packages changed in REVISION..HEAD instead of origin/TARGET..HEAD",
    )

    args = parser.parse_args()

    check_github_token()

    repo = Repo(".")

    if args.all:
        packages = list_all_packages(repo)
    else:
        revision = args.rev if args.rev else f"origin/{args.target}"
        packages = list_packages_to_check(repo, revision)
    packages = sorted(packages)

    eprint("Packages to check:")
    if not packages:
        eprint("None")
        return 0
    for package in packages:
        eprint(f"- {package}")

    if args.dry_run:
        return 0

    if args.target == "main":
        clyde_url = find_clyde_release_url()
    else:
        clyde_url = find_clyde_snapshot_url()

    download_clyde(clyde_url, CLYDE_DIR)
    check_packages(packages)
    return 0


if __name__ == "__main__":
    sys.exit(main())
# vi: ts=4 sw=4 et
