from pathlib import Path

from op_mt_tools.pipelines import add_text_pair_to_collection_pipeline

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Add text pairs to collection.")
    parser.add_argument(
        "collection_path",
        type=str,
        help="Path to the collection.",
    )
    args = parser.parse_args()

    add_text_pair_to_collection_pipeline(
        collection_path=Path(args.collection_path),
    )
