import os
import platform
import shutil
import sys
from pathlib import Path

IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"
IS_MACOS = platform.system() == "Darwin"

IS_AARCH64 = platform.machine() == "arm64"
IS_X86_64 = platform.machine() in {"x86_64", "AMD64"}


def which(cmd: str) -> str:
    cmd_path = shutil.which(cmd)
    if cmd_path is None:
        sys.exit(f"Can't find {cmd} in {os.environ['PATH']}")
    return cmd_path


def is_package(path: Path) -> bool:
    return path.suffix == ".yaml" and path.name[0] != "."
