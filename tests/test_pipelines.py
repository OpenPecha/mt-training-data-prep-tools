import os
from pathlib import Path
from unittest import mock

from op_mt_tools.pipelines import (
    download_text,
    download_textpairs_tracker_data,
    get_text_pairs,
)


def create_monlamAI_tracker_data(path, n):
    # create empty text pair file like BO0001.txt and EN0001.txt in tmp_path
    for i in range(1, n):
        bo_text_fn = path / f"BO{i:04d}"
        bo_text_fn.touch()
        if i % 2 == 0:
            en_text_fn = path / f"EN{i:04d}"
            en_text_fn.touch()
    return path


@mock.patch("op_mt_tools.pipelines.download_text")
def test_get_text_pairs(mock_download_text, tmp_path):
    path = create_monlamAI_tracker_data(tmp_path, 4)  # creates only BO0002 and EN0002
    text_download_path = tmp_path / "texts"
    mock_download_text.return_value = text_download_path

    text_pair_paths = list(get_text_pairs(path))

    assert text_pair_paths == [{"bo": text_download_path, "en": text_download_path}]
    assert mock_download_text.call_count == 2
    assert mock.call("BO0002") in mock_download_text.call_args_list
    assert mock.call("EN0002") in mock_download_text.call_args_list


@mock.patch("op_mt_tools.pipelines.clone_or_pull_repo")
def test_download_text(mock_clone_or_pull_repo):
    # arrange
    os.environ["GITHUB_USERNAME"] = "test"
    os.environ["GITHUB_TOKEN"] = "test"
    os.environ["MAI_GITHUB_ORG"] = "test"
    text_id = "BO0001"

    # act
    text_path = download_text(text_id)

    # assert
    assert text_path.name == text_id


@mock.patch("op_mt_tools.pipelines.clone_or_pull_repo")
def test_download_monlamAI_tracker_data(mock_clone_or_pull_repo):
    textpairs_tracker_path = download_textpairs_tracker_data()

    assert (
        textpairs_tracker_path
        == Path.home()
        / ".monlamAI"
        / "data"
        / "TRACKER"
        / "mt"
        / "mt-extracted-text-pairs"
    )
