from pathlib import Path

from .collection import Collection
from .utils import create_pecha


def add_text_pair_to_collection_pipeline(
    collection_path: Path, text_pair_path: Path
) -> None:
    """Add text pair to collection.

    Args:
        collection_path: Path to the collection.
        text_pair_path: Path to the text pair.
    """
    initial_pecha_id, open_pecha_id = create_pecha(text_pair_path)
    collection = Collection(path=collection_path)
    collection.set_pecha(open_pecha_id)
    collection.save()
