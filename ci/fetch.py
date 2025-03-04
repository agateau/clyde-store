#!/usr/bin/env python3
"""
Fetches updates for specified packages, push a branch with all modified packages.
"""
import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from get_clyde import download_clyde, find_clyde_snapshot_url
from git import Repo
from tui import progress
from utils import GIT_AUTHOR, get_modified_packages, list_all_packages


def run_clydetools_fetch(package_files: list[Path]) -> None:
    with TemporaryDirectory() as temp_dir:
        clyde_dir = Path(temp_dir) / "clyde"
        clyde_url = find_clyde_snapshot_url()
        download_clyde(clyde_url, clyde_dir)

        package_files = [x.absolute() for x in package_files]
        subprocess.run(
            ["clydetools", "fetch", *package_files], check=True, cwd=temp_dir
        )


def create_proposed_branch(repo: Repo, *, is_next: bool) -> str:
    """Create a branch and commit all modified packages to it.
    Returns the branch name.
    """
    base_branch = "next" if is_next else "main"
    timestamp = datetime.now().isoformat()
    timestamp_slug = timestamp.replace(":", "")
    branch_name = f"{base_branch}-proposed-{timestamp_slug}"

    progress(f"Creating proposed branch: '{branch_name}'")
    branch = repo.create_head(branch_name)
    branch.checkout()
    repo.index.add(get_modified_packages(repo))
    repo.index.commit(
        "Proposed updates for {base_branch} - {timestamp}",
        author=GIT_AUTHOR,
        committer=GIT_AUTHOR,
    )

    return branch_name


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter, description=__doc__
    )

    parser.add_argument(
        "--next",
        action="store_true",
        help="Target 'next' instead of 'main'",
    )

    parser.add_argument("package_files", nargs="*")

    args = parser.parse_args()

    if args.package_files:
        package_paths = [Path(x) for x in args.package_files]
    else:
        package_paths = list_all_packages()

    repo = Repo(Path("."))
    run_clydetools_fetch(package_paths)
    branch_name = create_proposed_branch(repo, is_next=args.next)

    progress("Pushing proposed branch")
    repo.git.push("-u", "origin", branch_name)

    return 0


if __name__ == "__main__":
    sys.exit(main())
# vi: ts=4 sw=4 et
