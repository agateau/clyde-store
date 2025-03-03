# About this directory

This directory contains CI scripts responsible for updating the store packages.

## How it works

### The Fetch workflow

Every day, the Fetch workflow is triggered. It runs `fetch.py`.

`fetch.py` looks for updates in all packages using `clydetools fetch`, commit the changes in a branch called `(main|target)-proposed-$DATE` and pushes this branch.

Pushing the proposed branch triggers the "Check proposed branch" workflow.

### The "Check proposed branch" workflow

This workflow runs `check_packages.py` on all supported OS.

`check_packages.py` runs `clydetools check` for each modified package and writes a report in a `check-$OS.json` file.

The workflow then gathers all `check-$OS.json` reports and run `merge_valid_changes.py`.

`merge_valid_changes.py` reverts the changes for the failed packages and commit the remaining changes to the target branch.
