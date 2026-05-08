#!/usr/bin/env python3
"""
Rebase auto-* branches and force-push them
"""

import argparse
import os
import sys
from tempfile import TemporaryDirectory
from typing import Iterable

from git import RemoteReference, Repo
from tui import eprint
from utils import mark_pr_as_automerge


def list_wanted_refs(
    repo: Repo, *, names: list[str] | None = None
) -> Iterable[RemoteReference]:
    for ref in repo.references:
        if ref.name.startswith("origin/auto-"):
            assert isinstance(ref, RemoteReference)
            if names:
                name = ref.name.split("/")[-1]
                if name not in names:
                    continue
            yield ref


def update_ref(repo: Repo, ref: RemoteReference) -> None:
    eprint("- Checkout")
    name = ref.name.split("/")[-1]
    repo.git.checkout(name)
    eprint("- Rebase")
    repo.git.rebase("main")
    eprint("- Push")
    repo.git.push(force_with_lease=True)
    eprint("- Mark as automerge")
    mark_pr_as_automerge(cwd=str(repo.working_dir))


def main() -> int:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter, description=__doc__
    )

    parser.add_argument("branches", nargs="*", help="Branches to rebase")
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="Rebase all auto-* branches",
    )
    parser.add_argument("-d", "--dry-run", action="store_true")

    args = parser.parse_args()

    with TemporaryDirectory("rebase-auto-XXXXXX") as dir:
        eprint("Cloning repo")
        url = f"file://{os.getcwd()}"
        repo = Repo.clone_from(url=url, to_path=dir)
        repo.remote().set_url("git@github.com:agateau/clyde-store")

        eprint("Fetching")
        repo.remote().fetch()

        if args.all:
            refs = list_wanted_refs(repo)
        else:
            refs = list_wanted_refs(repo, names=args.branches)
        refs = sorted(refs, key=lambda x: x.name)

        for ref in refs:
            eprint(f"Updating {ref}")

            if not args.dry_run:
                update_ref(repo, ref)

        return 0


if __name__ == "__main__":
    sys.exit(main())
# vi: ts=4 sw=4 et
