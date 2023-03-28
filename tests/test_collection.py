from datetime import datetime
from pathlib import Path
from unittest import mock

import pytest
from openpecha.core.layer import Layer, LayerEnum
from openpecha.core.pecha import OpenPechaGitRepo

from op_mt_tools.collection import (
    Collection,
    Metadata,
    View,
    ViewMetadata,
    ViewsEnum,
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


def test_collection_init_fail():
    with pytest.raises(ValueError):
        Collection()


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
        "views_path": "test",
    }
    assert metadata.to_dict() == ViewMetadata.from_dict(metadata.to_dict()).to_dict()


@mock.patch("openpecha.core.pecha.download_pecha")
def test_text_pair_plaintext_serializer(mock_download_pecha, tmp_path):
    # arrange

    # create pecha
    pecha_id = "P000001"
    pecha_path = Path(tmp_path) / pecha_id
    mock_download_pecha.return_value = pecha_path
    pecha = OpenPechaGitRepo(pecha_id=pecha_id)
    pecha._opf_path = pecha_path / f"{pecha_id}.opf"
    base_name = pecha.set_base("fake content")
    pecha.save_base()
    pecha.save_layer(
        base_name, LayerEnum.author, Layer(annotation_type=LayerEnum.author)
    )

    output_path = Path(tmp_path)
    text_pair = {"bo": pecha_id, "en": pecha_id}

    # act
    result = text_pair_plaintext_serializer(text_pair, output_path)

    # assert
    assert result == output_path
    assert (output_path / pecha_id / f"{base_name}-bo.txt").exists()
    assert (output_path / pecha_id / f"{base_name}-en.txt").exists()


@mock.patch("op_mt_tools.collection.text_pair_plaintext_serializer")
@mock.patch("op_mt_tools.collection.SERIALIZERS_REGISTRY")
def test_view_generate(mock_serializers_registery, mock_serialiser, tmp_path):
    # arrange
    mock_serialiser.return_value = tmp_path / "views" / ViewsEnum.PLAINTEXT
    mock_serializers_registery.get.return_value = mock_serialiser
    view_metadata = ViewMetadata(
        id=ViewsEnum.PLAINTEXT,
        serializer=ViewsEnum.PLAINTEXT,
        views_path=Path(f"views/{ViewsEnum.PLAINTEXT}/"),
    )
    view = View(base_path=(tmp_path / "views"), metadata=view_metadata)
    text_pair = {"bo": "P000001", "en": "P000002"}

    # act
    output_path = view.generate(text_pair)

    assert output_path == tmp_path / "views" / ViewsEnum.PLAINTEXT
    assert mock_serialiser.aseert_called_once_with(text_pair, output_path)


def test_view_init_fails():
    with pytest.raises(ValueError):
        View(base_path=Path("test"))


def test_view_construct_path_with_metadata():
    view_metadata = ViewMetadata(
        id=ViewsEnum.PLAINTEXT,
        serializer=ViewsEnum.PLAINTEXT,
        views_path=Path(f"views/{ViewsEnum.PLAINTEXT}/"),
    )
    view = View(base_path=Path("views"), metadata=view_metadata)
    assert view.path == Path("views") / ViewsEnum.PLAINTEXT


def test_view_load_metadata_with_id(tmp_path: Path):
    base_path = tmp_path / "views"
    view_metadata = ViewMetadata(
        id=ViewsEnum.PLAINTEXT,
        serializer=ViewsEnum.PLAINTEXT,
        views_path=Path(f"views/{ViewsEnum.PLAINTEXT}/"),
    )
    view = View(base_path=base_path, metadata=view_metadata)
    view.save_metadata()

    new_view = View(base_path=base_path, id=ViewsEnum.PLAINTEXT)

    assert new_view.metadata.to_dict() == view_metadata.to_dict()


def test_view_serializer_not_fount_exception(tmp_path):
    with pytest.raises(ValueError):
        view_metadata = ViewMetadata(
            id="fake-view_id",
            serializer="fake-serializer",
            views_path=Path("fake-views-path"),
        )
        view = View(base_path=tmp_path, metadata=view_metadata)
        view.generate({"bo": "pecha_id", "en": "pecha_id"})


def test_collection_views_path(tmp_path):
    collection_path = tmp_path / "test"
    c = Collection(collection_path)

    assert c.views_path == c.opa_path / "views"


@mock.patch("op_mt_tools.collection.View")
def test_collection_create_view(mock_view, tmp_path):
    collection_path = tmp_path / "test"
    view_path = tmp_path / "views" / ViewsEnum.PLAINTEXT
    mock_view_generate = mock.MagicMock()
    mock_view_generate.return_value = view_path
    mock_view.return_value.generate = mock_view_generate
    c = Collection(collection_path)
    text_pair = {"bo": "P000001", "en": "P000002"}
    c.create_view(view_id=ViewsEnum.PLAINTEXT, text_pair=text_pair)

    assert mock_view_generate.call_args.args[0] == text_pair
