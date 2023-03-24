from datetime import datetime
from pathlib import Path

import pytest

from op_mt_tools.collection import Collection, Metadata


@pytest.fixture
def collection_path():
    return Path("tests") / "data" / "collection"


def test_metadata():
    created_at = datetime.now()
    updated_at = datetime.now()

    metadata = Metadata(
        id="test",
        title="test",
        created_at=created_at,
        updated_at=updated_at,
        items=["P000001", "P000002"],
    )
    assert metadata.to_dict() == {
        "id": "test",
        "title": "test",
        "created_at": created_at,
        "updated_at": updated_at,
        "items": ["P000001", "P000002"],
    }
    assert metadata.to_dict() == Metadata.from_dict(metadata.to_dict()).to_dict()


def test_collection_set_pecha(collection_path):
    collection = Collection(collection_path)
    collection.set_pecha("P000001")
    assert collection.metadata.items == ["P000001"]


def test_collection_get_pechas(collection_path):
    collection = Collection(collection_path)
    collection.set_pecha("P000001")
    assert collection.get_pechas() == ["P000001"]
