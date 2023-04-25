import tempfile
from pathlib import Path
from unittest import mock

import pytest
from git.exc import GitCommandError

from op_mt_tools.utils import clone_or_pull_repo, commit_and_push, create_pecha


def test_create_pecha():
    # arrange
    text_path = Path("tests") / "data" / "text"

    # act
    with tempfile.TemporaryDirectory() as tmpdir:
        initial_pecha_id, open_pecha_id = create_pecha(
            text_path, publish=False, output_path=Path(tmpdir)
        )

    # assert
    assert initial_pecha_id
    assert open_pecha_id
    assert type(initial_pecha_id) == str
    assert type(open_pecha_id) == str


@mock.patch("op_mt_tools.utils.Repo")
def test_clone_repo_not_found(mock_repo_class):
    text_id = "BO0001"
    mock_repo_class.clone_from.side_effect = GitCommandError("git", "clone")
    repo_url = "https://github.com/test/test.git"
    local_repo_path = Path("tests") / "data" / "text_pair" / text_id

    # act and assert
    pytest.raises(ValueError, clone_or_pull_repo, repo_url, local_repo_path)


@mock.patch("op_mt_tools.utils.Repo")
def test_pull_repo(mock_repo_class, tmp_path):
    repo_url = "https://github.com/test/test.git"
    clone_or_pull_repo(repo_url, tmp_path)


@mock.patch("op_mt_tools.utils.Repo")
def test_commit_and_push(mock_repo_class):
    commit_and_push(Path("tests/data/text_pair/BO0001"))
