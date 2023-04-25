import os
import time
from collections import Counter
from collections.abc import Generator
from pathlib import Path

from . import config, tm
from . import types as t
from .collection import add_text_pair_to_collection
from .utils import clone_or_pull_repo, commit_and_push


def find_text_pair_ids(path: Path) -> Generator[t.TEXT_PAIR, None, None]:
    print("[INFO] Finding completed text pairs...")
    text_ids = [int(fn.name[2:]) for fn in path.iterdir() if fn.suffix != ".md"]
    counter = Counter(text_ids)
    text_pair_ids = [text_id for text_id, count in counter.items() if count == 2]
    for id_ in text_pair_ids:
        yield {"bo": f"BO{id_:04d}", "en": f"EN{id_:04d}"}


def download_text(text_id: t.TEXT_ID) -> Path:
    """Download text from monlamAI."""
    print(f"[INFO] Downloading text {text_id}...")
    github_username = os.environ["GITHUB_USERNAME"]
    github_token = os.environ["GITHUB_TOKEN"]
    github_org = os.environ["MAI_GITHUB_ORG"]
    text_repo_url = f"https://{github_username}:{github_token}@github.com/{github_org}/{text_id}.git"
    local_text_repo_path = config.DATA_PATH / "texts" / text_id
    clone_or_pull_repo(text_repo_url, local_text_repo_path)
    return local_text_repo_path


def download_text_pair(
    text_pair_ids: Generator[t.TEXT_PAIR, None, None],
) -> Generator[t.TEXT_PAIR_PATH, None, None]:
    """Download text pair from monlamAI."""
    print("[INFO] Downloading text pairs...")
    for text_pair_id in text_pair_ids:
        text_pair_path = {}
        for lang_code, text_id in text_pair_id.items():
            text_pair_path[lang_code] = download_text(text_id)
        yield text_pair_path


def download_textpairs_tracker_data() -> Path:
    """Download monlamAI tracker data."""
    print("[INFO] Downloading monlamAI tracker data...")

    github_org = os.environ["MAI_GITHUB_ORG"]
    tracker_repo_url = f"https://github.com/{github_org}/TRACKER.git"
    local_tracker_repo_path = config.DATA_PATH / "TRACKER"
    clone_or_pull_repo(tracker_repo_url, local_tracker_repo_path)
    textpairs_tracker_path = local_tracker_repo_path / "mt" / "mt-extracted-text-pairs"
    return textpairs_tracker_path


def get_text_pairs(path: Path) -> Generator[t.TEXT_PAIR_PATH, None, None]:
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


def add_text_pair_to_collection_pipeline(collection_path: Path) -> None:
    """Create collection from monlamAI text pair tracker.

    Args:
        path: Path to the monlamAI text pair tracker path.
        collection_path: Path to the collection.
    """
    print("[INFO] Pipeline running...")

    if not collection_path.is_dir():
        raise ValueError(f"Collection doesn't exist at {collection_path.resolve()}")

    text_pairs_tracker_path = download_textpairs_tracker_data()
    text_pair_paths = get_text_pairs(text_pairs_tracker_path)
    for text_pair_path in text_pair_paths:
        text_id, text_pair_view_path = add_text_pair_to_collection(
            text_pair_path, collection_path
        )
        if not text_id:
            continue
        commit_and_push(collection_path)
        time.sleep(3)
        tm.create_TM(text_pair_view_path, text_id)
