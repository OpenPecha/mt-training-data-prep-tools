import os
from pathlib import Path
from unittest import mock

from op_mt_tools.pipelines import (
    add_text_pair_to_collection_pipeline,
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
def test_get_text_pairs_from_tracker(mock_download_text, tmp_path):
    path = create_monlamAI_tracker_data(tmp_path, 4)  # creates only BO0002 and EN0002
    text_download_path = tmp_path / "texts"
    mock_download_text.return_value = True, text_download_path

    text_pair_paths = list(get_text_pairs(text_pairs_tracker_path=path))

    assert text_pair_paths == [{"bo": text_download_path, "en": text_download_path}]
    assert mock_download_text.call_count == 2
    assert mock.call("BO0002") in mock_download_text.call_args_list
    assert mock.call("EN0002") in mock_download_text.call_args_list


@mock.patch("op_mt_tools.pipelines.download_text")
def test_get_text_pairs_with_text_ids(mock_download_text, tmp_path):
    text_ids = ["0001", "0002"]
    text_download_path = tmp_path / "texts"
    mock_download_text.return_value = True, text_download_path

    text_pair_paths = list(get_text_pairs(text_ids=text_ids))

    assert text_pair_paths == [
        {"bo": text_download_path, "en": text_download_path},
        {"bo": text_download_path, "en": text_download_path},
    ]
    assert mock_download_text.call_count == 4
    assert mock.call("BO0001") in mock_download_text.call_args_list
    assert mock.call("EN0001") in mock_download_text.call_args_list
    assert mock.call("BO0002") in mock_download_text.call_args_list
    assert mock.call("EN0002") in mock_download_text.call_args_list


@mock.patch("op_mt_tools.pipelines.download_first_text_file_from_github_repo")
def test_download_text(mock_download_text_file):
    # arrange
    os.environ["GITHUB_USERNAME"] = "test"
    os.environ["GITHUB_TOKEN"] = "test"
    os.environ["MAI_GITHUB_ORG"] = "test"
    text_id = "BO0001"
    mock_download_text_file.return_value = Path(text_id)

    # act
    is_text_exists, text_path = download_text(text_id)

    # assert
    assert is_text_exists
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


@mock.patch("op_mt_tools.pipelines.download_textpairs_tracker_data")
@mock.patch("op_mt_tools.pipelines.get_text_pairs")
@mock.patch("op_mt_tools.pipelines.add_text_pair_to_collection")
@mock.patch("op_mt_tools.pipelines.commit_and_push")
@mock.patch("op_mt_tools.pipelines.create_TM")
def test_add_text_pair_to_collection_pipeline(
    create_TM,
    commit_and_push,
    add_text_pair_to_collection,
    get_text_pairs,
    download_textpairs_tracker_data,
):
    download_textpairs_tracker_data.return_value = Path("tests/data/text_pair")
    get_text_pairs.return_value = [
        {
            "bo": Path("tests/data/text_pair/BO0001"),
            "en": Path("tests/data/text_pair/EN0001"),
        }
    ]
    add_text_pair_to_collection.return_value = (
        "0001",
        {
            "bo": "C0001/C0001.opc/views/plaintext/O0001-bo.txt",
            "en": "C0001/C0001.opc/views/plaintext/O0002-en.txt",
        },
    )
    collection_path = Path("tests/data/collection")

    # act
    add_text_pair_to_collection_pipeline(collection_path)
