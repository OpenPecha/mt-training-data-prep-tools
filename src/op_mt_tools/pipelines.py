import os
import subprocess
from collections import Counter
from collections.abc import Generator
from pathlib import Path
from typing import Dict, Optional, Tuple

import requests
from git import Repo, cmd

from .collection import LANG_CODE, Collection, ViewsEnum
from .utils import create_pecha

TEXT_ID = str  # e.g. "BO0001" EN0001
TEXT_ID_NO_PREFIX = str  # e.g. "BO0001" -> "0001"
TEXT_PAIR = Dict[LANG_CODE, TEXT_ID]
TEXT_PAIR_PATH = Dict[LANG_CODE, Path]
TEXT_PAIR_VIEW_PATH = Dict[LANG_CODE, Path]

DATA_PATH = Path.home() / ".monlamAI" / "data"
DATA_PATH.mkdir(parents=True, exist_ok=True)


def find_text_pair_ids(path: Path) -> Generator[TEXT_PAIR, None, None]:
    print("[INFO] Finding completed text pairs...")
    text_ids = [int(fn.name[2:]) for fn in path.iterdir() if fn.suffix != ".md"]
    counter = Counter(text_ids)
    text_pair_ids = [text_id for text_id, count in counter.items() if count == 2]
    for id_ in text_pair_ids:
        yield {"bo": f"BO{id_:04d}", "en": f"EN{id_:04d}"}


def clone_or_pull_repo(repo_url: str, local_repo_path: Path) -> None:
    """Clone or pull repo."""
    if local_repo_path.is_dir():
        repo = Repo(local_repo_path)
        repo.remotes.origin.pull()
    else:
        try:
            Repo.clone_from(repo_url, str(local_repo_path))
        except cmd.GitCommandError as e:
            print(e)
            raise ValueError(f"Repo({repo_url}) doesn't exist")


def download_text(text_id: TEXT_ID) -> Path:
    """Download text from monlamAI."""
    print(f"[INFO] Downloading text {text_id}...")
    github_username = os.environ["GITHUB_USERNAME"]
    github_token = os.environ["GITHUB_TOKEN"]
    github_org = os.environ["MAI_GITHUB_ORG"]
    text_repo_url = f"https://{github_username}:{github_token}@github.com/{github_org}/{text_id}.git"
    local_text_repo_path = DATA_PATH / "texts" / text_id
    clone_or_pull_repo(text_repo_url, local_text_repo_path)
    return local_text_repo_path


def download_text_pair(
    text_pair_ids: Generator[TEXT_PAIR, None, None],
) -> Generator[TEXT_PAIR_PATH, None, None]:
    """Download text pair from monlamAI."""
    print("[INFO] Downloading text pairs...")
    for text_pair_id in text_pair_ids:
        text_pair_path = {}
        for lang_code, text_id in text_pair_id.items():
            text_pair_path[lang_code] = download_text(text_id)
        yield text_pair_path


def download_monlamAI_textpairs_tracker_data() -> Path:
    """Download monlamAI tracker data."""
    print("[INFO] Downloading monlamAI tracker data...")

    tracker_repo_url = "https://github.com/MonlamAI/TRACKER.git"
    local_tracker_repo_path = DATA_PATH / "TRACKER"
    clone_or_pull_repo(tracker_repo_url, local_tracker_repo_path)
    textpairs_tracker_path = local_tracker_repo_path / "mt" / "mt-extracted-text-pairs"
    return textpairs_tracker_path


def get_text_pairs(path: Path) -> Generator[TEXT_PAIR_PATH, None, None]:
    """Find text pairs id in `path` and download them.

    Args:
        path: Path to the monlamAI text pair tracker path.

    Returns:
        List of text pair paths.
    """
    print("[INFO] Getting text pairs...")
    text_pair_ids = find_text_pair_ids(path)
    text_pair_paths = download_text_pair(text_pair_ids)
    return text_pair_paths


def commit_and_push(collection_path: Path) -> None:
    """Commit and push collection."""
    # configure git users
    subprocess.run(f"git config --global user.name {os.environ['GITHUB_USERNAME']}")
    subprocess.run(f"git config --global user.email {os.environ['GITHUB_EMAIL']}")
    repo = Repo(collection_path)
    repo.git.add(".", "--all")
    repo.git.commit("-m", "Add text pair")
    repo.remotes.origin.push()


def add_text_pair_to_collection(
    text_pair_path: TEXT_PAIR_PATH, collection_path: Path
) -> Tuple[TEXT_ID_NO_PREFIX, TEXT_PAIR_VIEW_PATH]:
    """Add text pair to collection.

    Args:
        collection_path: Path to the collection.
        text_pair_path: Path to the text pair.
    """
    text_pair_ids = [fn.name for fn in text_pair_path.values()]
    collection = Collection(path=collection_path)
    text_id = text_pair_ids[0]
    if collection.is_text_added(text_id):
        print(f"[INFO] Text pair {text_pair_ids} is already to the collection...")
        return "", {}

    print(f"[INFO] Adding text pair {text_pair_ids} to the collection...")

    text_pair = {}
    output_path = DATA_PATH / "pechas"
    text_id = text_pair_ids[0]
    for lang_code, path in text_pair_path.items():
        _, open_pecha_id = create_pecha(path, output_path=output_path)
        text_pair[lang_code] = open_pecha_id

    text_pair = collection.add_text_pair(text_pair, text_id)
    collection.save()
    text_pair_view_path = collection.create_view(
        view_id=ViewsEnum.PLAINTEXT, text_pair=text_pair
    )
    commit_and_push(collection_path)
    return text_id[2:], text_pair_view_path


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


def create_monlamAI_TM(
    text_pair_view_path: Dict[LANG_CODE, Path], text_id: str
) -> Optional[dict]:
    request_body = {
        "text_id": text_id,
    }
    for lang_code, view_path in text_pair_view_path.items():
        request_body[f"{lang_code}_file_url"] = get_raw_github_file_url(view_path)

    r = requests.post(
        "https://openpecha-tibetan-aligner.hf.space/run/align",
        json={"data": [request_body]},
    )
    if r.status_code != requests.codes.ok:
        print(f"[ERROR] Failed to algin {text_id}. Error code {r.status_code}")
        return None
    else:
        return r.json()["data"]


def add_text_pair_to_collection_pipeline(collection_path: Path) -> None:
    """Create collection from monlamAI text pair tracker.

    Args:
        path: Path to the monlamAI text pair tracker path.
        collection_path: Path to the collection.
    """
    print("[INFO] Pipeline running...")

    if not collection_path.is_dir():
        raise ValueError(f"Collection doesn't exist at {collection_path.resolve()}")

    text_pairs_tracker_path = download_monlamAI_textpairs_tracker_data()
    text_pair_paths = get_text_pairs(text_pairs_tracker_path)
    for text_pair_path in text_pair_paths:
        text_id, text_pair_view_path = add_text_pair_to_collection(
            text_pair_path, collection_path
        )
        if not text_id:
            continue
        create_monlamAI_TM(text_pair_view_path, text_id)
