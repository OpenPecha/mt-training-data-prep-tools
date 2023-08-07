import json
from pathlib import Path
from unittest import mock

import pytest
from gradio_client.utils import Status as JobStatus

from op_mt_tools.tm import (
    create_request_body,
    create_TM,
    get_client,
    get_raw_github_file_url,
    run_aligner,
)


@pytest.mark.skip()
def test_get_client_two_client():
    client_1 = get_client(max_clients=2)
    client_2 = get_client(max_clients=2)
    client_3 = get_client(max_clients=2)

    assert client_1
    assert client_2
    assert client_3 == client_1


def test_get_raw_github_file_url(tmp_path):
    view_path = tmp_path / "C1A81F448/C1A81F448.opc/views/plaintext/O192F059E-bo.txt"

    raw_gh_file_url = get_raw_github_file_url(view_path)

    assert (
        raw_gh_file_url
        == "https://raw.githubusercontent.com/OpenPecha-Data/C1A81F448/main/C1A81F448.opc/views/plaintext/O192F059E-bo.txt"  # noqa
    )


@mock.patch("op_mt_tools.tm.get_client")
def test_run_aligner(mock_get_client):
    input_json_fn = Path("test.json")
    job_mock = mock.MagicMock(name="job_mock")
    job_mock.status.return_value.code = JobStatus.PROCESSING
    client_mock = mock.MagicMock(name="client_mock")
    client_mock.submit.return_value = job_mock
    mock_get_client.return_value = client_mock

    status = run_aligner(input_json_fn)

    assert status == "PROCESSING"


def test_create_request_body(tmp_path):
    en_view_path = tmp_path / "C1A81F448/C1A81F448.opc/views/plaintext/O192F059E-en.txt"
    bo_view_path = tmp_path / "C1A81F448/C1A81F448.opc/views/plaintext/O66BF9EDC-bo.txt"

    text_pair_view_path = {"bo": bo_view_path, "en": en_view_path}
    request_body_fn = create_request_body(
        text_id="text_id", text_pair_view_path=text_pair_view_path, base_dir=tmp_path
    )

    assert request_body_fn.exists()
    assert json.loads(request_body_fn.read_text()) == {
        "text_id": "text_id",
        "bo_file_url": "https://raw.githubusercontent.com/OpenPecha-Data/C1A81F448/main/C1A81F448.opc/views/plaintext/O66BF9EDC-bo.txt",  # noqa
        "en_file_url": "https://raw.githubusercontent.com/OpenPecha-Data/C1A81F448/main/C1A81F448.opc/views/plaintext/O192F059E-en.txt",  # noqa
    }


@mock.patch("op_mt_tools.tm.create_request_body")
@mock.patch("op_mt_tools.tm.run_aligner")
def test_create_monlamAI_TM(mock_run_aligner, mock_create_request_body, tmp_path):
    # arrange
    text_pair_view_path = {"bo": tmp_path, "en": tmp_path}
    mock_run_aligner.return_value = "PROCESSING"
    mock_create_request_body.return_value = tmp_path / "request.json"
    status = create_TM(text_id="text_id", text_pair_view_path=text_pair_view_path)
    assert status == "PROCESSING"

    mock_run_aligner.asssert_called_once_with(tmp_path / "request.json")
    assert mock_create_request_body.call_args[0][0] == "text_id"
    assert mock_create_request_body.call_args[0][1] == text_pair_view_path
