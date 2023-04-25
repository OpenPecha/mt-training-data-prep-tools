import os
from pathlib import Path
from unittest import mock

import pytest
from git.cmd import GitCommandError

from op_mt_tools.collection import Collection, Metadata
from op_mt_tools.pipelines import (
    add_text_pair_to_collection,
    download_monlamAI_textpairs_tracker_data,
    download_text,
    get_text_pairs,
)


@mock.patch("op_mt_tools.pipelines.commit_and_push")
@mock.patch("op_mt_tools.collection.View")
@mock.patch("op_mt_tools.pipelines.create_pecha")
def test_add_text_pair_to_collection(
    mock_create_pecha, mock_view, mock_commit_and_push, tmp_path
):
    # IGNORE: arrange boilerplate
    collection_id = "collection"
    metadata = Metadata(
        id=collection_id,
        title="collection",
    )
    collection = Collection(metadata=metadata)
    collection.save(output_path=tmp_path)
    mock_view_generate = mock.MagicMock()
    mock_view_generate.return_value = tmp_path / "views" / "plaintext"
    mock_view.return_value.generate = mock_view_generate

    # arrange
    collection_path = tmp_path / collection_id
    text_pair = {
        "bo": Path("tests") / "data" / "text_pair" / "bo" / "P000001",
        "en": Path("tests") / "data" / "text_pair" / "en" / "P000002",
    }
    mock_create_pecha.return_value = ("I001", "O001")

    # act
    text_id, text_pair_view_path = add_text_pair_to_collection(
        text_pair, collection_path
    )

    # assert
    collection = Collection(collection_path)
    assert {"bo": "O001", "en": "O001"} in collection.metadata.items


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


@mock.patch("op_mt_tools.pipelines.Repo")
def test_download_text(mock_repo_class):
    # arrange
    os.environ["GITHUB_USERNAME"] = "test"
    os.environ["GITHUB_TOKEN"] = "test"
    os.environ["MAI_GITHUB_ORG"] = "test"
    text_id = "BO0001"

    # act
    text_path = download_text(text_id)

    # assert
    assert text_path.name == text_id


@mock.patch("op_mt_tools.pipelines.Repo")
def test_download_text_text_not_found(mock_repo_class):
    text_id = "BO0001"
    mock_repo_class.clone_from.side_effect = GitCommandError("git", "clone")

    # act and assert
    pytest.raises(ValueError, download_text, text_id)


@mock.patch("op_mt_tools.pipelines.Repo")
def test_download_monlamAI_tracker_data(mock_repo_class):
    mock_repo_class.clone_from.return_value = None
    textpairs_tracker_path = download_monlamAI_textpairs_tracker_data()

    assert (
        textpairs_tracker_path
        == Path.home()
        / ".monlamAI"
        / "data"
        / "TRACKER"
        / "mt"
        / "mt-extracted-text-pairs"
    )
