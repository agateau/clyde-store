from pathlib import Path

import pytest
from git import Repo
from utils import get_target_branch


@pytest.mark.parametrize(
    ["current_branch", "expected_target"],
    (
        ("main-proposed-2022", "main"),
        ("next-proposed-2024", "next"),
        ("main", None),
    ),
)
def test_get_target_branch(
    tmp_path: Path, current_branch: str, expected_target: str | None
):
    repo = Repo.init(tmp_path)
    repo.index.commit("Empty commit")
    repo.create_head(current_branch).checkout()

    if expected_target:
        assert get_target_branch(repo) == expected_target
    else:
        with pytest.raises(ValueError):
            get_target_branch(repo)
