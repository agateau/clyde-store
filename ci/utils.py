import os
import platform
import shutil
import sys

IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"
IS_MACOS = platform.system() == "Darwin"


def which(cmd: str) -> str:
    cmd_path = shutil.which(cmd)
    if cmd_path is None:
        sys.exit(f"Can't find {cmd} in {os.environ['PATH']}")
    return cmd_path
