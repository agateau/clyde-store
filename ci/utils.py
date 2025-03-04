import itertools
import os
import platform
import shutil
import sys
from collections.abc import Iterable
from pathlib import Path

from git import Actor, Repo

IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"
IS_MACOS = platform.system() == "Darwin"

IS_AARCH64 = platform.machine() == "arm64"
IS_X86_64 = platform.machine() in {"x86_64", "AMD64"}

CI_DIR = Path(__file__).parent.resolve()
CLYDE_DIR = CI_DIR / "clyde"
ROOT_DIR = CI_DIR.parent.resolve()

GIT_AUTHOR = Actor("ClydeStore bot", "clydestore@agateau.com")


def which(cmd: str) -> str:
    cmd_path = shutil.which(cmd)
    if cmd_path is None:
        sys.exit(f"Can't find {cmd} in {os.environ['PATH']}")
    return cmd_path


def is_package(path: Path) -> bool:
    return (
        path.suffix == ".yaml" and path.name[0] != "." and ".github" not in path.parts
    )


def get_modified_packages(repo: Repo) -> Iterable[Path]:
    diff_index = repo.index.diff(None)
    for diff in diff_index.iter_change_type("M"):
        path = Path(diff.b_path)
        if is_package(path):
            yield path


def get_target_branch(repo: Repo) -> str:
    name = repo.head.reference.name
    if name.startswith("main-proposed-"):
        return "main"
    if name.startswith("next-proposed-"):
        return "next"
    raise ValueError(f"Current branch ({name}) is not a proposed branch")


def list_all_packages() -> list[Path]:
    return [
        x
        for x in itertools.chain(
            ROOT_DIR.glob("*.yaml"),
            ROOT_DIR.glob("*/index.yaml"),
            ROOT_DIR.glob("packages/*.yaml"),
            ROOT_DIR.glob("packages/*/index.yaml"),
        )
        if is_package(x)
    ]
