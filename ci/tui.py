import sys


if sys.stdout.isatty():
    CYAN = "\033[36m"
    RESET = "\033[0;0m"
else:
    CYAN = ""
    RESET = ""


def eprint(msg: str) -> None:
    print(msg, file=sys.stderr)


def progress(msg: str) -> None:
    eprint(f"{CYAN}{msg}{RESET}")
