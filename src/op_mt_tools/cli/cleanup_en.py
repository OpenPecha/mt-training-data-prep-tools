import argparse
import os

from op_mt_tools import config
from op_mt_tools.cleanup import (
    cleanup_en,
    find_failed_cleanup_chunks,
    split_chunk_into_sentence,
)
from op_mt_tools.github_utils import clone_or_pull_repo, commit_and_push

GITHUB_ORG = os.environ["MAI_GITHUB_ORG"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]


def run_batch_cleanup(args):
    for text_id in args.text_ids:
        text_dir = config.TEXTS_PATH / text_id
        print(f"[INFO] Downloading {text_id} ...")
        clone_or_pull_repo(
            repo=text_id, org=GITHUB_ORG, token=GITHUB_TOKEN, local_path=text_dir
        )

        print(f"[INFO] Cleaning {text_id} ...")
        for i, text_fn in enumerate(text_dir.glob("*.txt")):
            cleaned_fn = cleanup_en(text_fn, verbose=args.verbose)
            print(f"[INFO] Pushing cleaned text {text_id} ...")
            print(f"[INFO] Cleaned text is saved at {cleaned_fn} ...")

        if not args.skip_push:
            print(f"[INFO] Committing and pushing {text_id} ...")
            commit_and_push(text_dir, msg="auto cleanup")


def run_failed_chunks(args):
    text_path = config.TEXTS_PATH / args.text_id
    failed_chunks = find_failed_cleanup_chunks(text_path, overlap=args.overlap)
    print(
        f"[INFO] Failed chunks based on {args.overlap} overlap percent: \n- {failed_chunks}"
    )
    failed_percent = len(failed_chunks) / (failed_chunks[-1])
    print(f"[INFO] Total failed chunks: {failed_percent:.2f}")


def run_sent_tokenizer(args):
    text_path = config.TEXTS_PATH / args.text_id
    split_chunk_into_sentence(text_path)


def main():
    parser = argparse.ArgumentParser(
        description="Clean up English text using OpenAI GPT"
    )
    subparsers = parser.add_subparsers(dest="command")

    batch_cleanup = subparsers.add_parser("batch_cleanup", help="run batch cleanup")
    batch_cleanup.add_argument(
        "text_ids",
        nargs="+",
        help="list of text ids to clean up",
    )
    batch_cleanup.add_argument(
        "--verbose",
        action="store_true",
    )
    batch_cleanup.add_argument(
        "--skip_push",
        action="store_true",
    )

    find_failed_chunks = subparsers.add_parser(
        "find_failed_chunks", help="find failed chunks"
    )
    find_failed_chunks.add_argument(
        "text_id", help="text id to find failed chunks for", type=str
    )
    find_failed_chunks.add_argument(
        "--overlap",
        type=float,
        default=0.8,
        help="char count overlap percent between cleaned and unclead chunks",
    )

    sent_tokenize = subparsers.add_parser("sent_tok", help="split chunk into sentences")
    sent_tokenize.add_argument(
        "text_id", help="text id to chunks into sentence", type=str
    )

    args = parser.parse_args()
    if args.command == "batch_cleanup":
        run_batch_cleanup(args)
    elif args.command == "find_failed_chunks":
        run_failed_chunks(args)
    elif args.command == "sent_tok":
        run_sent_tokenizer(args)


if __name__ == "__main__":
    main()
