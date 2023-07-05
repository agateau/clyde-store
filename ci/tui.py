import sys

if sys.stdout.isatty():
    ORANGE = "\033[33m"
    CYAN = "\033[36m"
    RESET = "\033[0;0m"
else:
    ORANGE = ""
    CYAN = ""
    RESET = ""


def eprint(msg: str) -> None:
    print(msg, file=sys.stderr)


def progress(msg: str) -> None:
    eprint(f"{CYAN}{msg}{RESET}")


def warning(msg: str) -> None:
    eprint(f"{ORANGE}{msg}{RESET}")
