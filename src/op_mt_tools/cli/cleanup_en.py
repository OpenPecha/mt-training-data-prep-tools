import argparse
import os

from op_mt_tools import config
from op_mt_tools.cleanup import cleanup_en
from op_mt_tools.github_utils import clone_or_pull_repo, commit_and_push

GITHUB_ORG = os.environ["MAI_GITHUB_ORG"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Clean up English text using OpenAI GPT"
    )
    parser.add_argument(
        "text_ids",
        nargs="+",
        help="list of text ids to clean up",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
    )
    parser.add_argument(
        "--skip_push",
        action="store_true",
    )
    args = parser.parse_args()

    for text_id in args.text_ids:
        text_dir = config.TEXTS_PATH / text_id
        print(f"[INFO] Downloading text {text_id}")
        clone_or_pull_repo(
            repo=text_id, org=GITHUB_ORG, token=GITHUB_TOKEN, local_path=text_dir
        )
        for i, text_fn in enumerate(text_dir.glob("*.txt")):
            print(f"\t- Cleaning up text file {i:04}...")
            cleaned_fn = cleanup_en(text_fn, verbose=args.verbose)

        if not args.skip_push:
            print(f"[INFO] Pushing cleaned text {text_id}...")
            commit_and_push(text_dir)
