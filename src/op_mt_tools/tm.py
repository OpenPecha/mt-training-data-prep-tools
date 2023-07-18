import argparse
import json
import logging
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional

from gradio_client import Client
from gradio_client.utils import Status as JobStatus

from . import types as t
from .github_utils import commit_and_push, get_github_repos_with_prefix

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


def get_all_TMs() -> Optional[List[str]]:
    """Get all latest TMs."""
    org = os.environ["MAI_GITHUB_ORG"]
    token = os.environ["GITHUB_TOKEN"]
    repos = get_github_repos_with_prefix(org, token, "TM")
    return repos


def export_TM(tm: str, export_dir: Path, branch):
    """Export TM as submodules of `output_dir`."""
    tm_url = f"https://github.com/{os.environ['MAI_GITHUB_ORG']}/{tm}.git"
    submodule_path = f"{tm}"
    subprocess.run(
        ["git", "submodule", "add", "-b", branch, "--force", tm_url, submodule_path],
        cwd=export_dir,
    )


def export_all_TMs(
    export_dir: Path,
    tm_ids: Optional[List[t.TEXT_ID]] = None,
    branch: str = "main",
):
    """Export all latest TMs."""
    print("[INFO] Exporting all TMs...")

    if not tm_ids:
        tm_ids = get_all_TMs()

    if not tm_ids:
        print("[INFO] No TM found. Exiting...")
        return

    for tm_id in tm_ids:
        if not tm_id:
            continue
        if export_dir.joinpath(tm_id).exists():
            print(f"[INFO] {tm_id} already exists. Skipping...")
            continue
        export_TM(tm_id, export_dir, branch)

    msg = "add TMs on " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    commit_and_push(export_dir, msg)
    print("[INFO] Exporting all TMs done!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("export_dir", type=Path, default=".")
    parser.add_argument(
        "--tm_ids",
        nargs="+",
        help="add only these text",
    )
    parser.add_argument(
        "--branch",
        default="main",
        help="default branch of the TM repo",
    )
    parser.add_argument(
        "--not-tm",
        action="store_true",
    )
    args = parser.parse_args()

    export_all_TMs(args.export_dir, tm_ids=args.tm_ids, branch=args.branch)
