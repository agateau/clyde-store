import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import BinaryIO, Dict, Pattern
from urllib import request

from tui import eprint, progress
from utils import IS_MACOS, IS_WINDOWS, which

GITHUB_TOKEN = os.getenv("CLYDE_GITHUB_TOKEN", "")

CLYDE_SNAPSHOT_LIST_URL = "https://builds.agateau.com/clyde/"
CLYDE_RELEASE_LIST_URL = "https://api.github.com/repos/agateau/clyde/releases/latest"

CURL_RETRY = 3


def _create_request(url: str, headers: Dict[str, str]) -> request.Request:
    req = request.Request(url)
    for key, value in headers.items():
        req.add_header(key, value)

    return req


def _http_get(url: str) -> BinaryIO:
    eprint(f"get {url}")
    headers = {
        "User-Agent": "clyde-store-check-packages",
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    req = _create_request(url, headers)
    return request.urlopen(req)  # type: ignore


def _get_archive_rx() -> Pattern[str]:
    if IS_WINDOWS:
        archive_ext_rx = r"\.zip"
    else:
        archive_ext_rx = r"\.tar\.gz"

    if IS_WINDOWS:
        os_name = "windows"
    elif IS_MACOS:
        os_name = "macos"
    else:
        os_name = "linux"

    return re.compile(f"clyde-[-_a-zT0-9.+]*-{os_name}{archive_ext_rx}")


def find_clyde_release_url() -> str:
    progress("Looking for archive of latest Clyde release")
    response = _http_get(CLYDE_RELEASE_LIST_URL)
    dct = json.load(response)
    archives_url = [x["browser_download_url"] for x in dct["assets"]]
    archive_rx = _get_archive_rx()
    for url in archives_url:
        if archive_rx.search(url):
            assert isinstance(url, str)
            return url
    sys.exit(f"Can't find URL from\n{json.dumps(dct, indent=2)}")


def find_clyde_snapshot_url() -> str:
    progress(f"Looking for snapshot Clyde archive on {CLYDE_SNAPSHOT_LIST_URL}")
    content = str(_http_get(CLYDE_SNAPSHOT_LIST_URL).read())
    match = _get_archive_rx().search(content)
    if not match:
        sys.exit("Could not find archive")
    archive_name = match.group(0)

    return f"{CLYDE_SNAPSHOT_LIST_URL}{archive_name}"


def download_clyde(url: str, clyde_dir: Path) -> None:
    if clyde_dir.exists():
        shutil.rmtree(clyde_dir)
    clyde_dir.mkdir()

    archive_path = clyde_dir / ("clyde.zip" if IS_WINDOWS else "clyde.tar.gz")
    progress(f"Downloading archive from {url}")
    subprocess.run(
        [which("curl"), "--retry", str(CURL_RETRY), "-L", url, "-o", str(archive_path)],
        check=True,
    )

    progress("Unpacking archive")
    if IS_WINDOWS:
        cmd = [which("7z"), "e", "-bb0", str(archive_path)]
    else:
        cmd = [which("tar"), "--strip-components=1", "-xzf", str(archive_path)]
    subprocess.run(cmd, check=True, cwd=clyde_dir)

    os.environ["PATH"] = str(clyde_dir) + os.pathsep + os.environ["PATH"]
