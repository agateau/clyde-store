from pathlib import Path

from check_packages import list_packages_to_check
from git import Repo


def test_list_packages_to_check(tmp_path: Path):
    # GIVEN a repo with a CI dir and packages
    repo = Repo.init(tmp_path)
    repo.index.commit("Empty commit")

    (tmp_path / "ci").mkdir()
    (tmp_path / "packages").mkdir()
    (tmp_path / "ci/script.py").touch()

    for x in range(4):
        (tmp_path / f"packages/{x}.yaml").write_text(f"created {x}")
    repo.index.add(("ci", "packages"))
    repo.index.commit("Import")

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
