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

ROOT_DIR = Path(__file__).parent.parent.resolve()
CLYDE_DIR = ROOT_DIR / "ci/clyde"

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
        assert diff.b_path
        path = Path(diff.b_path)
        if is_package(path):
            yield path


def list_all_packages(repo: Repo) -> list[Path]:
    root_dir = Path(repo.working_tree_dir)
    return [
        x
        for x in itertools.chain(
            root_dir.glob("*.yaml"),
            root_dir.glob("*/index.yaml"),
            root_dir.glob("packages/*.yaml"),
            root_dir.glob("packages/*/index.yaml"),
        )
        if is_package(x)
    ]
