import os
import time
from collections import Counter
from collections.abc import Generator
from functools import partial
from pathlib import Path
from typing import Callable, Optional, Tuple

from . import config
from . import types as t
from .collection import add_text_pair_to_collection, skip_text
from .github_utils import download_first_text_file_from_github_repo
from .tm import create_TM
from .utils import clone_or_pull_repo, commit_and_push


def find_text_pair_ids(path: Path) -> Generator[t.TEXT_PAIR, None, None]:
    print("[INFO] Finding completed text pairs...")
    text_ids = [int(fn.name[2:]) for fn in path.iterdir() if fn.suffix != ".md"]
    counter = Counter(text_ids)
    text_pair_ids = [text_id for text_id, count in counter.items() if count == 2]
    for id_ in text_pair_ids:
        yield {"bo": f"BO{id_:04d}", "en": f"EN{id_:04d}"}


def download_text(text_id: t.TEXT_ID) -> Tuple[bool, Path]:
    """Download text from monlamAI.

    Args:
        text_id: The text id.

    Returns:
        text_file_exists: Whether the text file exists.
        local_text_repo_path: The local path to the text repository.
    """
    print(f"[INFO] Downloading text {text_id}...")
    github_token = os.environ["GITHUB_TOKEN"]
    github_org = os.environ["MAI_GITHUB_ORG"]
    local_text_repo_path = config.DATA_PATH / "texts" / text_id
    local_text_repo_path.mkdir(parents=True, exist_ok=True)
    text_file_fn = download_first_text_file_from_github_repo(
        repo_owner=github_org,
        repo_name=text_id,
        token=github_token,
        output_path=local_text_repo_path,
    )
    text_file_exists = text_file_fn is not None
    return text_file_exists, local_text_repo_path


def download_text_pair(
    text_pair_ids: Generator[t.TEXT_PAIR, None, None],
    skip_text_callback: Optional[Callable] = None,
) -> Generator[t.TEXT_PAIR_PATH, None, None]:
    """Download text pair from monlamAI."""
    print("[INFO] Downloading text pairs...")
    for text_pair_id in text_pair_ids:
        text_pair_path = {}
        for lang_code, text_id in text_pair_id.items():
            if skip_text_callback and skip_text_callback(text_id=text_id):
                continue
            text_file_exists, text_path = download_text(text_id)
            if not text_file_exists:
                break
            text_pair_path[lang_code] = text_path

        # only return text pair path if both texts exist
        if len(text_pair_path) == 2:
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


def get_text_pairs(
    path: Path, skip_text_callback: Optional[Callable] = None
) -> Generator[t.TEXT_PAIR_PATH, None, None]:
    """Find text pairs id in `path` and download them.

    Args:
        path: Path to the monlamAI text pair tracker path.

    Returns:
        List of text pair paths.
    """
    print("[INFO] Getting text pairs...")
    text_pair_ids = find_text_pair_ids(path)
    text_pair_paths = download_text_pair(text_pair_ids, skip_text_callback)
    return text_pair_paths


def add_text_pair_to_collection_pipeline(
    collection_path: Path,
    should_create_TM=True,
    run_for_first_n_texts: float = float("inf"),
) -> None:
    """Create collection from monlamAI text pair tracker.

    Args:
        path: Path to the monlamAI text pair tracker path.
        collection_path: Path to the collection.
    """
    print("[INFO] Pipeline running...")

    if not collection_path.is_dir():
        raise ValueError(f"Collection doesn't exist at {collection_path.resolve()}")

    text_pairs_tracker_path = download_textpairs_tracker_data()
    skip_text_callback = partial(skip_text, collection_path=collection_path)
    text_pair_paths = get_text_pairs(text_pairs_tracker_path, skip_text_callback)
    n_texts = 0
    for text_pair_path in text_pair_paths:
        if n_texts >= run_for_first_n_texts:
            break
        text_id, text_pair_view_path = add_text_pair_to_collection(
            text_pair_path, collection_path
        )
        if not text_id:
            continue
        commit_and_push(collection_path)
        time.sleep(3)
        if should_create_TM:
            create_TM(text_pair_view_path, text_id)
        n_texts += 1
