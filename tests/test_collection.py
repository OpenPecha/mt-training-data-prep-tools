from datetime import datetime
from pathlib import Path
from unittest import mock

import pytest
from openpecha.core.layer import Layer, LayerEnum
from openpecha.core.metadata import OpenPechaMetadata
from openpecha.core.pecha import OpenPechaGitRepo

from op_mt_tools.collection import (
    Collection,
    Metadata,
    ViewMetadata,
    text_pair_plaintext_serializer,
)


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


def test_view_metadata():
    created_at = datetime.now()
    updated_at = datetime.now()

    metadata = ViewMetadata(
        id="test",
        serializer="test",
        views_path=Path("test"),
        created_at=created_at,
        updated_at=updated_at,
    )
    assert metadata.to_dict() == {
        "id": "test",
        "created_at": created_at,
        "updated_at": updated_at,
        "serializer": "test",
        "views_path": Path("test"),
    }
    assert metadata.to_dict() == ViewMetadata.from_dict(metadata.to_dict()).to_dict()


@mock.patch("openpecha.core.pecha.download_pecha")
def test_text_pair_plaintext_serializer(mock_download_pecha, tmp_path):
    # arrange
    metadata = OpenPechaMetadata()
    pecha_path = Path(tmp_path) / metadata.id
    mock_download_pecha.return_value = pecha_path
    pecha = OpenPechaGitRepo(pecha_id=metadata.id, metadata=metadata)
    pecha._opf_path = pecha_path / f"{metadata.id}.opf"
    base_name = pecha.set_base("fake content")
    pecha.save_base()
    pecha.save_layer(
        base_name, LayerEnum.author, Layer(annotation_type=LayerEnum.author)
    )
    pecha_id = metadata.id
    output_path = Path(tmp_path)
    text_pair = {"bo": pecha_id, "en": pecha_id}
    result = text_pair_plaintext_serializer(text_pair, output_path)

    assert result == output_path
    assert (output_path / pecha_id / f"{base_name}-bo.txt").exists()
    assert (output_path / pecha_id / f"{base_name}-en.txt").exists()
