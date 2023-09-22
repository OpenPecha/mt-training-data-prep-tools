import logging
import re
from pathlib import Path
from typing import List, Optional

from op_mt_tools import config
from op_mt_tools.github_utils import create_github_repo_from_dir
from op_mt_tools.logger import setup_logger

SOURCE_NAME = "84000"

logger_name = "import.84000.text_pair"
logger_path = setup_logger(logger_name)


def get_text_pair_files(path: Path):
    for bo_text_fn in path.glob("*-bo-plain.txt"):
        en_text_fn = path / bo_text_fn.name.replace("bo", "en")
        if not en_text_fn.exists():
            continue
        yield bo_text_fn, en_text_fn


def get_source_id(fn, prefix):
    return fn.stem.split(f"-{prefix.lower()}")[0]


def get_text_id(fn: Path, prefix: str) -> str:
    source_id = get_source_id(fn, prefix)
    return f"{prefix}{source_id}_{SOURCE_NAME}"


def get_text(fn: Path) -> str:
    return "\n".join(fn.read_text().splitlines()[1:])


def save_text(src_text_fn: Path, text_id: str):
    text_path = config.TEXTS_PATH / text_id
    text_path.mkdir(parents=True, exist_ok=True)
    dest_text_fn = text_path / f"{text_id}.txt"
    text = get_text(src_text_fn)
    dest_text_fn.write_text(text)

    try:
        create_github_repo_from_dir(text_path)
    except Exception as e:
        logging.error(f"Error in creating github repo {text_id}")
        logging.error(e)
        return
    logging.info(f"Imported Text: {text_id}")


def save_text_pair(bo_text_fn: Path, en_text_fn: Path):
    bo_text_id = get_text_id(bo_text_fn, "BO")
    en_text_id = get_text_id(en_text_fn, "EN")

    save_text(bo_text_fn, bo_text_id)
    save_text(en_text_fn, en_text_id)


def import_text_pairs(path: Path, text_ids: Optional[List[str]] = None):
    for bo_text_fn, en_text_fn in get_text_pair_files(path):
        source_id = get_source_id(bo_text_fn, "BO")
        if text_ids and source_id not in text_ids:
            continue
        save_text_pair(bo_text_fn, en_text_fn)


def print_success_tms():
    logs = logger_path.read_text()
    pattern = r"Imported Text: (.*_84000)"
    tm_ids = re.findall(pattern, logs)
    for tm_id in tm_ids:
        print(tm_id)


def print_failed_tms():
    logs = logger_path.read_text()
    pattern = r"Error in creating github repo (.*_84000)"
    tm_ids = re.findall(pattern, logs)
    for tm_id in tm_ids:
        print(tm_id)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Import 84000 Text Pairs")
    parser.add_argument(
        "--path",
        type=str,
        help="Path to the 84000 Text Pair directory",
    )

    parser.add_argument(
        "--text-ids",
        nargs="+",
        help="List of 84000 text ids to import",
    )

    parser.add_argument(
        "--get-success-tms",
        action="store_true",
        help="Get all TM ids that are successfully imported",
    )
    parser.add_argument(
        "--get-failed-tms",
        action="store_true",
        help="Get all TM ids that are failed to import",
    )

    args = parser.parse_args()
    if args.path:
        import_text_pairs(Path(args.path), args.text_ids)
    elif args.get_success_tms:
        print_success_tms()
    elif args.get_failed_tms:
        print_failed_tms()
    else:
        parser.print_help()
