from collections import Counter
from collections.abc import Generator
from pathlib import Path
from typing import Dict

from .collection import LANG_CODE, Collection, ViewsEnum
from .utils import create_pecha

TEXT_ID = str
TEXT_PAIR = Dict[LANG_CODE, TEXT_ID]
TEXT_PAIR_PATH = Dict[LANG_CODE, Path]


def find_text_pair_ids(path: Path) -> Generator[TEXT_PAIR, None, None]:
    text_ids = [int(fn.name[2:]) for fn in path.iterdir() if fn.suffix != ".md"]
    counter = Counter(text_ids)
    text_pair_ids = [text_id for text_id, count in counter.items() if count == 2]
    for id_ in text_pair_ids:
        yield {"bo": f"BO{id_:04d}", "en": f"EN{id_:04d}"}


def download_text_pair(text_id: str) -> Path:
    return Path("texts") / text_id


def get_text_pairs(path: Path) -> Generator[TEXT_PAIR_PATH, None, None]:
    """Find text pairs id in `path` and download them.

    Args:
        path: Path to the monlamAI text pair tracker path.

    Returns:
        List of text pair paths.
    """
    text_pair_ids = find_text_pair_ids(path)
    for text_pair_id in text_pair_ids:
        text_pair_path = {}
        for lang_code, text_id in text_pair_id.items():
            text_pair_path[lang_code] = download_text_pair(text_id)
        yield text_pair_path


def add_text_pair_to_collection_pipeline(
    text_pair_path: Dict[LANG_CODE, Path], collection_path: Path
) -> None:
    """Add text pair to collection.

    Args:
        collection_path: Path to the collection.
        text_pair_path: Path to the text pair.
    """
    text_pair = {}
    for lang_code, path in text_pair_path.items():
        _, open_pecha_id = create_pecha(path)
        text_pair[lang_code] = open_pecha_id
    collection = Collection(path=collection_path)
    text_pair = collection.add_text_pair(text_pair)
    collection.save()
    collection.create_view(view_id=ViewsEnum.PLAINTEXT, text_pair=text_pair)
