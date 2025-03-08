from pathlib import Path

from check_packages import list_packages_to_check
from git import Repo


def create_test_repo(tmp_path: Path):
    repo = Repo.init(tmp_path)
    repo.index.commit("Empty commit")

    (tmp_path / "ci").mkdir()
    (tmp_path / "packages").mkdir()
    (tmp_path / "ci/script.py").touch()

    for x in range(4):
        (tmp_path / f"packages/{x}.yaml").write_text(f"created {x}")
    repo.index.add(("ci", "packages"))
    repo.index.commit("Import")
    return repo


def test_list_packages_to_check_only_packages(tmp_path: Path):
    # GIVEN a test repo
    repo = create_test_repo(tmp_path)

    # AND a commit modifying two packages
    for x in range(2):
        (tmp_path / f"packages/{x}.yaml").write_text(f"modified {x}")
    repo.index.add("packages")
    repo.index.commit("Modified")

    # WHEN list_packages_to_check() is called
    packages = list_packages_to_check(repo, "HEAD^")

    # THEN it returns the two packages
    expected = [Path(f"packages/{x}.yaml") for x in range(2)]
    assert packages == expected


def test_list_packages_to_check_only_ci(tmp_path: Path):
    # GIVEN a test repo
    repo = create_test_repo(tmp_path)

    # AND a commit modifying the CI script
    ci_script_path = tmp_path / "ci/script.py"
    ci_script_path.write_text("Script modification")
    repo.index.add(ci_script_path)
    repo.index.commit("Modified")

    # WHEN list_packages_to_check() is called
    random_count = 2
    packages = list_packages_to_check(repo, "HEAD^", random_count=random_count)

    # THEN it returns a random combination of packages
    existing_packages = list((tmp_path / "packages").glob("*.yaml"))
    for package in packages:
        assert package in existing_packages
    assert len(packages) == random_count
