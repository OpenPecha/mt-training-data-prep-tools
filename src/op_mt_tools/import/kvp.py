import logging
import re
import shutil
from pathlib import Path

from op_mt_tools import config
from op_mt_tools.github_utils import create_github_repo_from_dir
from op_mt_tools.logger import setup_logger

SOURCE_NAME = "KVP"

logger_name = "import.kvp"
logger_path = setup_logger(logger_name)


def get_text_pair_files(path: Path):
    for bo_text_fn in path.glob("*_bo.txt"):
        en_text_fn = path / bo_text_fn.name.replace("bo", "en")
        if not en_text_fn.exists():
            continue
        yield bo_text_fn, en_text_fn


def get_text_id(fn: Path, prefix: str) -> str:
    soruce_id = fn.stem.split("_")[0]
    return f"{prefix}{soruce_id}_{SOURCE_NAME}"


def save_text(src_text_fn: Path, text_id: str):
    text_path = config.TEXTS_PATH / text_id
    text_path.mkdir(parents=True, exist_ok=True)
    text_fn_cp = text_path / f"{text_id}.txt"
    shutil.copyfile(str(src_text_fn), str(text_fn_cp))
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


def import_text_pairs(path: Path):
    for bo_text_fn, en_text_fn in get_text_pair_files(path):
        save_text_pair(bo_text_fn, en_text_fn)


def print_success_tms():
    logs = logger_path.read_text()
    pattern = r"Imported Text: (.*_KVP)"
    tm_ids = re.findall(pattern, logs)
    for tm_id in tm_ids:
        print(tm_id)


def print_failed_tms():
    logs = logger_path.read_text()
    pattern = r"Error in creating github repo (.*_KVP)"
    tm_ids = re.findall(pattern, logs)
    for tm_id in tm_ids:
        print(tm_id)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Import KVP Text Pairs")
    parser.add_argument(
        "--path",
        type=str,
        help="Path to the KVP Text Pair directory",
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
        import_text_pairs(Path(args.path))
    elif args.get_success_tms:
        print_success_tms()
    elif args.get_failed_tms:
        print_failed_tms()
    else:
        parser.print_help()
