from pathlib import Path

import yaml
from fetch import create_proposed_branch, run_clydetools_fetch
from git import Repo

CURRENT_REPO_DIR = Path(__name__).absolute().parent.parent
assert (CURRENT_REPO_DIR / ".git").exists()

PACKAGES_DIR = CURRENT_REPO_DIR / "packages"


def downgrade_package(dct: dict[str, object]):
    # Keep only the first release of a package
    releases = dct["releases"]
    version, assets = list(releases.items())[0]
    dct["releases"] = {version: assets}


def test_run_clydetools_fetch(tmp_path: Path):
    test_packages = ["ripgrep.yaml", "fd.yaml"]

    # Copy some package files and keep only their first releease
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
        dct = yaml.safe_load(src_path.read_text())
        assert len(dct["releases"]) > 1


def test_create_proposed_branch(tmp_path: Path):
    # Setup a repo
    repo = Repo.clone_from(CURRENT_REPO_DIR, tmp_path)

    # Make changes to some packages
    # Does not matter if the changes are valid YAML
    packages_dir = tmp_path / "packages"
    modified_package_paths = list(packages_dir.rglob("*.yaml"))[:3]
    for package_path in modified_package_paths:
        package_path.write_text("Changed")

    # Run create_proposed_branch
    name = create_proposed_branch(repo, is_next=False)

    # Check branch name
    assert name.startswith("main-proposed-20")

    # Check branch content
    diff_index = repo.head.commit.diff("HEAD~1")
    modified_files = [Path(x.b_path) for x in diff_index.iter_change_type("M")]
    assert sorted(modified_files) == sorted(
        x.relative_to(tmp_path) for x in modified_package_paths
    )
    assert not repo.is_dirty()
