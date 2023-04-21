from pathlib import Path
from typing import Dict, Optional

import requests

from . import types as t


def get_raw_github_file_url(local_view_path: Path):
    """Get raw github file url.

    Args:
        view_file: Path to the view file. eg: parent/C1A81F448/C1A81F448.opc/views/plaintext/O192F059E/6555-en.txt

    Returns:
        Raw github file url.
    """
    local_view_fn = list(local_view_path.iterdir())[0]
    repo_name = local_view_fn.parts[-6]
    view_fn = "/".join(local_view_fn.parts[-5:])
    return (
        f"https://raw.githubusercontent.com/OpenPecha-Data/{repo_name}/main/{view_fn}"
    )


def create_TM(
    text_pair_view_path: Dict[t.LANG_CODE, Path], text_id: str
) -> Optional[dict]:
    def create_request_body(text_id, text_pair_view_path):
        request_body = {
            "text_id": text_id,
        }
        for lang_code, view_path in text_pair_view_path.items():
            request_body[f"{lang_code}_file_url"] = get_raw_github_file_url(view_path)

    request_body = create_request_body(text_id, text_pair_view_path)
    r = requests.post("https://api.monlam.ai/mt/create-tm", json=request_body)

    if r.status_code != requests.codes.ok:
        print(f"[ERROR] Failed to algin {text_id}. Error code {r.status_code}")
        return None
    else:
        return r.json()["data"]
