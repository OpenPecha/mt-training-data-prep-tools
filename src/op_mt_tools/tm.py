import json
import logging
import tempfile
import time
from pathlib import Path
from typing import Dict

from gradio_client import Client
from gradio_client.utils import Status as JobStatus

from . import types as t

client = None


def get_client():
    global client
    if not client:
        client = Client("openpecha/tibetan-aligner-api")
    return client


def run_aligner(input_json_fn: Path):
    client = get_client()
    job = client.submit(
        input_json_fn,
        api_name="/align",
    )

    logging.info("Waiting for Alignment Job to start...")
    while job.status().code != JobStatus.PROCESSING:
        time.sleep(1)
    logging.info("Alignment Job started")
    return "PROCESSING"


def get_raw_github_file_url(local_view_fn: Path):
    """Get raw github file url.

    Args:
        view_file: Path to the view file. eg: parent/C1A81F448/C1A81F448.opc/views/plaintext/O192F059E/6555-en.txt

    Returns:
        Raw github file url.
    """
    local_view_fn = Path(local_view_fn)
    repo_name = local_view_fn.parts[-5]
    view_fn = "/".join(local_view_fn.parts[-4:])
    return (
        f"https://raw.githubusercontent.com/OpenPecha-Data/{repo_name}/main/{view_fn}"
    )


def create_request_body(text_id, text_pair_view_path, base_dir: Path) -> Path:
    """Create request body for TM creation.

    Args:
        text_id: Text id.
        text_pair_view_path: Dict of language code and view path.

    Returns:
        request_json_fn(Path): Request body saved in json.
    """
    request_body = {
        "text_id": text_id,
    }
    for lang_code, view_path in text_pair_view_path.items():
        request_body[f"{lang_code}_file_url"] = get_raw_github_file_url(view_path)

    request_body_json_fn = base_dir / "request_body.json"
    json.dump(request_body, request_body_json_fn.open("w"))
    return request_body_json_fn


def create_TM(text_pair_view_path: Dict[t.LANG_CODE, Path], text_id: str) -> str:
    with tempfile.TemporaryDirectory() as tmp_dir:
        request_body_json_fn = create_request_body(
            text_id, text_pair_view_path, base_dir=Path(tmp_dir)
        )
        status = run_aligner(request_body_json_fn)
        return status
