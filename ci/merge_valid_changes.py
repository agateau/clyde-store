#!/usr/bin/env python3
"""
Look at all `clydetools check` reports, revert changes for failed packages,
then merge the changes.
"""
import argparse
import json
import sys
from pathlib import Path

from git import Repo
from utils import get_target_branch


def revert_failed_changes(repo: Repo, report_paths: list[Path]) -> None:
    to_revert_paths = set()
    for path in report_paths:
        report = json.loads(path.read_text())
        for fail in report.get("fails", []):
            to_revert_paths.add(fail)

    if not to_revert_paths:
        return

    # Get previous commit
    it = repo.iter_commits()
    _ = next(it)
    previous = next(it)

    # Revert changes locally
    for path in to_revert_paths:
        repo.git.checkout(previous, path)
        repo.index.add(path)

    # Amend commit
    repo.git.commit("--amend", "--no-edit")


def merge_branch(repo: Repo, target_branch: str) -> None:
    source_branch = repo.head.reference.name
    repo.git.checkout(target_branch)
    repo.git.merge(source_branch)


def main() -> int:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter, description=__doc__
    )

    parser.add_argument("reports", nargs="+")

    args = parser.parse_args()

    repo = Repo(Path("."))
    try:
        target_branch = get_target_branch(repo)
    except ValueError as e:
        sys.exit(str(e))

    revert_failed_changes(repo, [Path(x) for x in args.reports])

    merge_branch(repo, target_branch)

    return 0


if __name__ == "__main__":
    sys.exit(main())
# vi: ts=4 sw=4 et
