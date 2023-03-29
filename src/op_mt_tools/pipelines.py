import os
from collections import Counter
from collections.abc import Generator
from pathlib import Path
from typing import Dict

from git import Repo, cmd

from .collection import LANG_CODE, Collection, ViewsEnum
from .utils import create_pecha

TEXT_ID = str
TEXT_PAIR = Dict[LANG_CODE, TEXT_ID]
TEXT_PAIR_PATH = Dict[LANG_CODE, Path]


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
    github_username = os.environ["MAI_GITHUB_USERNAME"]
    github_token = os.environ["MAI_GITHUB_TOKEN"]
    github_org = os.environ["MAI_GITHUB_ORG"]
    text_repo_url = f"https://{github_username}:{github_token}@github.com/{github_org}/{text_id}.git"
    local_text_repo_path = Path.home() / github_org / text_id
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
    local_tracker_repo_path = Path.home() / "MonlamAI" / "TRACKER"
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


def add_text_pair_to_collection(
    text_pair_path: Dict[LANG_CODE, Path], collection_path: Path
) -> None:
    """Add text pair to collection.

    Args:
        collection_path: Path to the collection.
        text_pair_path: Path to the text pair.
    """
    text_pair_ids = [fn.name for fn in text_pair_path.values()]
    print(f"[INFO] Adding text pair {text_pair_ids} to the collection...")
    text_pair = {}
    for lang_code, path in text_pair_path.items():
        _, open_pecha_id = create_pecha(path)
        text_pair[lang_code] = open_pecha_id
    collection = Collection(path=collection_path)
    text_pair = collection.add_text_pair(text_pair)
    collection.save()
    collection.create_view(view_id=ViewsEnum.PLAINTEXT, text_pair=text_pair)


def add_text_pair_to_collection_pipeline(collection_path: Path) -> None:
    """Create collection from monlamAI text pair tracker.

    Args:
        path: Path to the monlamAI text pair tracker path.
        collection_path: Path to the collection.
    """
    print("[INFO] Pipeline running...")
    text_pairs_tracker_path = download_monlamAI_textpairs_tracker_data()
    text_pair_paths = get_text_pairs(text_pairs_tracker_path)
    for text_pair_path in text_pair_paths:
        add_text_pair_to_collection(text_pair_path, collection_path)
