# About this directory

This directory contains CI scripts responsible for updating the store packages.

## How it works

### The fetch workflow

Every day, the fetch workflow is triggered. It runs `clydetools fetch` and open individual PRs for each modified package. These PRs are marked as auto-merge.

### The "check-packages-main" workflow

This workflow runs on main and on each PR targeting it.

For each supported Arch-Os, it runs `clydetools check` on the modified package.

Since the PRs opened by the fetch workflow are marked as auto-merge, the changes are then merged in the main branch.
