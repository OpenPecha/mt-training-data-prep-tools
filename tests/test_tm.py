from unittest import mock

from op_mt_tools.tm import create_TM, get_raw_github_file_url


def test_get_raw_github_file_url(tmp_path):
    view_path = tmp_path / "C1A81F448/C1A81F448.opc/views/plaintext/O192F059E"
    view_path.mkdir(parents=True)
    view_fn = view_path / "test-en.txt"
    view_fn.write_text("test content")

    raw_gh_file_url = get_raw_github_file_url(view_path)

    assert (
        raw_gh_file_url
        == "https://raw.githubusercontent.com/OpenPecha-Data/C1A81F448/main/C1A81F448.opc/views/plaintext/O192F059E/test-en.txt"  # noqa
    )


@mock.patch("op_mt_tools.tm.requests")
def test_create_monlamAI_TM(mock_requests, tmp_path):
    en_view_path = tmp_path / "C1A81F448/C1A81F448.opc/views/plaintext/O192F059E"
    en_view_path.mkdir(parents=True)
    en_view_fn = en_view_path / "6555-en.txt"
    en_view_fn.write_text("test content")
    bo_view_path = tmp_path / "C1A81F448/C1A81F448.opc/views/plaintext/O66BF9EDC"
    bo_view_path.mkdir(parents=True)
    bo_view_fn = bo_view_path / "BAF9-bo.txt"
    bo_view_fn.write_text("test content")

    text_pair_view_path = {"bo": bo_view_path, "en": en_view_path}

    data = create_TM(text_id="test_form_tools", text_pair_view_path=text_pair_view_path)
    assert not data
