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
        items=[{"bo": "P000001", "en": "P000002"}],
    )
    assert metadata.to_dict() == {
        "id": "test",
        "title": "test",
        "created_at": created_at,
        "updated_at": updated_at,
        "items": [{"bo": "P000001", "en": "P000002"}],
    }
    assert metadata.to_dict() == Metadata.from_dict(metadata.to_dict()).to_dict()


def test_collection_add_text_pair(collection_path):
    collection = Collection(collection_path)
    collection.add_text_pair({"bo": "P000001", "en": "P000002"})
    assert collection.metadata.items == [{"bo": "P000001", "en": "P000002"}]


def test_collection_get_text_pairs(collection_path):
    collection = Collection(collection_path)
    collection.add_text_pair({"bo": "P000001", "en": "P000002"})
    assert collection.get_text_pairs() == [{"bo": "P000001", "en": "P000002"}]


def test_collection_save(tmp_path):
    collection_path = tmp_path / "test"
    metadata = Metadata(
        id="test",
        title="test",
    )
    collection = Collection(
        metadata=metadata,
    )
    collection.add_text_pair({"bo": "P000001", "en": "P000002"})
    collection.save(output_path=tmp_path)
    assert collection.meta_fn.exists()

    collection = Collection(collection_path)
    assert collection.metadata.items == [{"bo": "P000001", "en": "P000002"}]


def test_collection_create_new(tmp_path):
    metadata = Metadata(
        title="test",
    )
    collection = Collection(metadata=metadata)
    collection.add_text_pair({"bo": "P000001", "en": "P000002"})
    collection.save(output_path=tmp_path)

    assert collection.meta_fn.exists()
