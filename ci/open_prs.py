#!/usr/bin/env python3
"""
Files individual PRs for each modified package.
"""

import argparse
import subprocess
import sys
from pathlib import Path

from git import Repo
from tui import progress, warning
from utils import get_modified_packages


def has_remote_branch(repo: Repo, branch: str) -> bool:
    output = repo.git.branch("--remote", "--list", f"origin/{branch}")
    return output.strip() != ""


def file_pr(repo: Repo, path: Path, base_branch: str):
    name = path.stem
    if name == "index":
        name = path.parent.name

    branch_name = f"auto-update-{name}"
    already_exists = has_remote_branch(repo, branch_name)
    if already_exists:
        warning(f"Branch {branch_name} already exists, overwriting it")

    repo.git.checkout("-B", branch_name, base_branch)

    repo.index.add(path)
    repo.index.commit(f"Update {name}")

    # Push
    push_args = ["-u", "origin", branch_name]
    if already_exists:
        push_args.append("--force-with-lease")
    repo.git.push(*push_args)

    # Open PR
    if not already_exists:
        subprocess.run(
            ["gh", "pr", "create", "--fill", "--base", base_branch], check=True
        )
        subprocess.run(["gh", "pr", "merge", "--auto", "-dm"], check=True)
    repo.git.checkout("-")


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter, description=__doc__
    )

    parser.add_argument(
        "--next",
        action="store_true",
        help="Target 'next' instead of 'main'",
    )

    args = parser.parse_args()

    repo = Repo(".")

    base_branch = "next" if args.next else "main"
    for package in get_modified_packages(repo):
        progress(f"Filing PR for {package}")
        file_pr(repo, package, base_branch)

    return 0


if __name__ == "__main__":
    sys.exit(main())
# vi: ts=4 sw=4 et
