#!/usr/bin/env python3
"""
Check packages changed between TARGET and HEAD are valid.
"""
import argparse
import itertools
import random
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List

from get_clyde import (
    GITHUB_TOKEN,
    download_clyde,
    find_clyde_release_url,
    find_clyde_snapshot_url,
)
from tui import eprint, progress
from utils import is_package, which

CI_DIR = Path(__file__).parent.resolve()
CLYDE_DIR = CI_DIR / "clyde"
ROOT_DIR = CI_DIR.parent.resolve()

RANDOM_COUNT = 8


def check_github_token() -> None:
    if not GITHUB_TOKEN:
        eprint(
            "CLYDE_GITHUB_TOKEN environment variable not set. Consider defining it"
            " to avoid being rate-limited."
        )


def iter_modified_files(revision: str) -> Iterable[Path]:
    cmd = ["git", "diff", "--raw", revision, "HEAD"]
    proc = subprocess.run(cmd, check=True, stdout=subprocess.PIPE)
    out = str(proc.stdout, "utf-8")
    for line in out.split("\n"):
        match = re.search("([A-Z]+)\\d*\t([^\\s]+)$", line)
        if match:
            status, path_str = match.groups()
            if status not in {"R", "D"}:
                yield Path(path_str).resolve()


def has_ci_changed(paths: List[Path]) -> bool:
    return any(CI_DIR in x.parents for x in paths)


def list_all_packages() -> List[Path]:
    return [
        x
        for x in itertools.chain(ROOT_DIR.glob("*.yaml"), ROOT_DIR.glob("*/index.yaml"))
        if is_package(x)
    ]


def list_packages_to_check(revision: str) -> List[Path]:
    progress("Listing packages to check")
    paths = list(iter_modified_files(revision))
    packages = [x for x in paths if is_package(x)]
    if has_ci_changed(paths):
        eprint(
            f"CI files have changed: adding a random selection of {RANDOM_COUNT} packages"
        )
        all_packages = list_all_packages()
        candidates = list(set(all_packages) - set(packages))
        if len(candidates) <= RANDOM_COUNT:
            return all_packages
        packages.extend(random.sample(candidates, RANDOM_COUNT))
    return packages


def check_packages(packages: List[Path], report_path: str | None) -> int:
    # We must run the test in the current directory for now
    package_names = [x.relative_to(ROOT_DIR) for x in packages]
    cmd = [which("clydetools"), "check"] + package_names
    if report_path:
        cmd.extend(["--report", report_path])
    proc = subprocess.run(cmd, cwd=ROOT_DIR)
    return proc.returncode


def main() -> int:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter, description=__doc__
    )

    parser.add_argument(
        "target",
        metavar="TARGET",
        choices=["main", "next"],
        help="The target branch. Must be 'main' or 'next'",
    )
    parser.add_argument("-a", "--all", action="store_true")
    parser.add_argument("-d", "--dry-run", action="store_true")
    parser.add_argument(
        "--rev",
        metavar="REVISION",
        help="Check packages changed in REVISION..HEAD instead of origin/TARGET..HEAD",
    )
    parser.add_argument(
        "-r", "--report", help="Path where to store a clydetools check report"
    )

    args = parser.parse_args()

    check_github_token()

    if args.all:
        packages = list_all_packages()
    else:
        revision = args.rev if args.rev else f"origin/{args.target}"
        packages = list_packages_to_check(revision)
    packages = sorted(packages)

    eprint("Packages to check:")
    if not packages:
        eprint("None")
        return 0
    for package in packages:
        eprint(f"- {package.relative_to(ROOT_DIR)}")

    if args.dry_run:
        return 0

    if args.target == "main":
        clyde_url = find_clyde_release_url()
    else:
        clyde_url = find_clyde_snapshot_url()

    download_clyde(clyde_url, CLYDE_DIR)
    return check_packages(packages, args.report)


if __name__ == "__main__":
    sys.exit(main())
# vi: ts=4 sw=4 et
