from pathlib import Path
from typing import Dict

from .collection import LANG_CODE, Collection, ViewsEnum
from .utils import create_pecha


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
