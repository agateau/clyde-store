import json
from pathlib import Path

from git import Repo
from merge_valid_changes import revert_failed_changes


def test_revert_failed_changes(tmp_path: Path):
    # GIVEN a repo with 3 packages, p1, p2 and p3
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    repo = Repo.init(repo_path)
    package_paths = [repo_path / f"p{x}.yaml" for x in range(3)]
    for path in package_paths:
        path.write_text(f"name: {path.stem}\n")
        repo.index.add(path)
    repo.index.commit("Init")

    # AND the packages have been modified
    for path in package_paths:
        path.write_text(f"name: {path.stem}\nname2: {path.stem}\n")
        repo.index.add(path)
    repo.index.commit("Proposed changes")

    # AND a report with a failure on p0
    report1 = tmp_path / "report1.json"
    report1.write_text(json.dumps({"fails": ["p0.yaml"]}))

    # AND another report with a failure on p0 and p1
    report2 = tmp_path / "report1.json"
    report2.write_text(json.dumps({"fails": ["p0.yaml", "p1.yaml"]}))

    # WHEN revert_failed_changes() is called on the reports
    revert_failed_changes(repo, [report1, report2])

    # THEN p0 and p1 changes are reverted
    assert not repo.is_dirty()
    assert package_paths[0].read_text() == "name: p0\n"
    assert package_paths[1].read_text() == "name: p1\n"

    # AND p2 changes are kept
    assert package_paths[2].read_text() == "name: p2\nname2: p2\n"


def test_merge_branch():
    pass
