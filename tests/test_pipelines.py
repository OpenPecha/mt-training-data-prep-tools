from unittest import mock

from op_mt_tools.collection import Collection, Metadata
from op_mt_tools.pipelines import add_text_pair_to_collection_pipeline


@mock.patch("op_mt_tools.pipelines.create_pecha")
def test_add_text_pair_to_collection_pipeline(mock_create_pecha, tmp_path):
    # arrange
    collection_id = "collection"
    collection_path = tmp_path / collection_id
    text_pair_path = tmp_path / "text_pair"

    metadata = Metadata(
        id=collection_id,
        title="collection",
    )
    collection = Collection(metadata=metadata)
    collection.save(tmp_path)

    mock_create_pecha.return_value = ("I000001", "O000002")
    add_text_pair_to_collection_pipeline(collection_path, text_pair_path)

    collection = Collection(collection_path)
    assert "O000002" in collection.metadata.items
