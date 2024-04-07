# Clyde Store

This repository contains package definitions for [Clyde][], the prebuilt application package manager.

[Clyde]: https://github.com/agateau/clyde

## Requesting a new package

If an application you need is missing from the store, you can request a new package for it by filling an [issue on this repository][request-package].

[request-package]: https://github.com/agateau/clyde-store/issues/new?template=package.md

## Creating a new package

You want to create a new package yourself? Awesome! You can get started by following the [package tutorial][tutorial] on Clyde repository, then opening a Pull Request here.

[tutorial]: https://github.com/agateau/clyde/blob/main/docs/creating-a-package.md

## Branches

The `main` branch is the one used by default by Clyde. All package definitions in this branch must work with the currently released version of Clyde.

The `next` branch can be used for package definitions which use syntaxes not yet understood by the released version of Clyde. When a new version of Clyde is released, the `next` branch is merged in the `main` branch.
