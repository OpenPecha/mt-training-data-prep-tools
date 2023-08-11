import os
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
    parser.add_argument(
        "--skip_create_TM",
        action="store_true",
        help="whether to create TM",
    )
    parser.add_argument(
        "--text_ids",
        nargs="+",
        help="add only these text",
    )
    parser.add_argument(
        "--gpt_cleaned",
        action="store_true",
        help="whether to use gpt cleaned text",
    )
    args = parser.parse_args()

    add_text_pair_to_collection_pipeline(
        collection_path=Path(args.collection_path),
        should_create_TM=False if args.skip_create_TM else True,
        text_ids=args.text_ids,
    )

    # for gradio_client threading
    os._exit(0)
