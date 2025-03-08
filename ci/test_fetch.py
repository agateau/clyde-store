from pathlib import Path
from typing import cast

import yaml
from fetch import run_clydetools_fetch

CURRENT_REPO_DIR = Path(__file__).absolute().parent.parent
assert (CURRENT_REPO_DIR / ".git").exists()

PACKAGES_DIR = CURRENT_REPO_DIR / "packages"


def downgrade_package(dct: dict[str, object]):
    # Keep only the first release of a package
    releases = cast(dict[str, object], dct["releases"])
    version, assets = list(releases.items())[0]
    dct["releases"] = {version: assets}


def test_run_clydetools_fetch(tmp_path: Path):
    test_packages = ["ripgrep.yaml", "fd.yaml"]

    # Copy some package files and keep only their first release
    modified_package_paths = []
    for package_name in test_packages:
        src_path = PACKAGES_DIR / package_name
        dct = yaml.safe_load(src_path.read_text())
        assert len(dct["releases"]) > 1

        downgrade_package(dct)
        assert len(dct["releases"]) == 1

        dst_path = tmp_path / package_name
        dst_path.write_text(yaml.dump(dct))

        modified_package_paths.append(dst_path)

    # Run run_clydetools_fetch
    run_clydetools_fetch(modified_package_paths)

    # Check the packages have more than one release again (don't check they
    # have the same release because there might have been a new one in between)
    for path in modified_package_paths:
        dct = yaml.safe_load(path.read_text())
        assert len(dct["releases"]) > 1
