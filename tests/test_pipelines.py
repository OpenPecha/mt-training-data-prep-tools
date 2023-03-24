from pathlib import Path
from unittest import mock

from op_mt_tools.collection import Collection, Metadata
from op_mt_tools.pipelines import add_text_pair_to_collection_pipeline


@mock.patch("op_mt_tools.pipelines.create_pecha")
def test_add_text_pair_to_collection_pipeline(mock_create_pecha, tmp_path):
    # IGNORE: arrange boilerplate
    collection_id = "collection"
    metadata = Metadata(
        id=collection_id,
        title="collection",
    )
    collection = Collection(metadata=metadata)
    collection.save(output_path=tmp_path)

    # arrange
    collection_path = tmp_path / collection_id
    text_pair = {
        "bo": Path("tests") / "data" / "text_pair" / "bo" / "P000001",
        "en": Path("tests") / "data" / "text_pair" / "en" / "P000002",
    }
    mock_create_pecha.return_value = ("I001", "O001")

    # act
    add_text_pair_to_collection_pipeline(text_pair, collection_path)

    # assert
    collection = Collection(collection_path)
    assert {"bo": "O001", "en": "O001"} in collection.metadata.items
