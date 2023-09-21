import logging
import re
from pathlib import Path
from typing import Optional

from op_mt_tools import config
from op_mt_tools.github_utils import commit_and_push, download_monlanai_repo
from op_mt_tools.logger import setup_logger

logger_name = "qc.clean_84000"
logger_path = setup_logger(logger_name)


def download_tm(tm_id):
    tm_path = config.TMS_PATH / tm_id
    tm_path = download_monlanai_repo(tm_id, tm_path)
    return tm_path


def download_text_repo(text_id):
    text_repo_path = config.TEXTS_PATH / text_id
    text_repo_path = download_monlanai_repo(text_id, text_repo_path)
    return text_repo_path


def tm_id2text_id(tm_id: str, lang: str):
    return f"{lang}{tm_id[2:]}"


def clean_tm(tm_id: str):
    def get_tm_text(tm_path: Path, lang: str):
        text_fn = list(tm_path.glob(f"*-{lang.lower()}.txt"))[0]
        return text_fn.read_text(), text_fn

    def clean_bo(text):
        text = text.replace("input_text", "")
        text = re.sub(r"\{\{.*\}\}", "", text)
        return text.strip()

    def clean_en(text):
        text = text.replace("target_text", "")
        text = re.sub(r"\{\{.*\}\}", "", text)
        return text.strip()

    tm_path = download_tm(tm_id)
    bo_text, bo_text_fn = get_tm_text(tm_path, "bo")
    en_text, en_text_fn = get_tm_text(tm_path, "en")
    bo_text_cleaned = clean_bo(bo_text)
    en_text_cleaned = clean_en(en_text)

    if bo_text_cleaned.count("\n") != en_text_cleaned.count("\n"):
        logging.error(f"Number of segments do not match in {tm_id}")
        return

    bo_text_fn.write_text(bo_text_cleaned)
    en_text_fn.write_text(en_text_cleaned)

    return tm_path


def clean_text_repo(tm_id: str, lang: str):
    text_id = tm_id2text_id(tm_id, lang)
    try:
        text_repo_path = download_text_repo(text_id)
    except Exception:
        logging.error(f"Error in downloading {text_id}")
        return
    text_fns = list(text_repo_path.glob("*.txt"))

    if not text_fns:
        logging.error(f"Error in downloading {text_id}")
        return

    text_fn = text_fns[0]
    text = text_fn.read_text()
    text = re.sub(r"\{\{.*\}\}", "", text)
    text_fn.write_text(text.strip())
    return text_repo_path


def push_repo(repo_path: Optional[Path], log_msg: str):
    if not repo_path:
        logging.error(f"Failed to clean {log_msg}")
        return
    try:
        commit_and_push(repo_path, "Cleaned")
    except Exception:
        logging.error(f"Error in pushing {repo_path.name}")
        return


def run_pipeline(args):
    for tm_id in args.tm_ids:
        logging.info(f"Processing {tm_id}")
        tm_path = clean_tm(tm_id)
        bo_text_path = clean_text_repo(tm_id, "BO")
        en_text_path = clean_text_repo(tm_id, "EN")
        if not args.no_push:
            push_repo(tm_path, tm_id)
            push_repo(bo_text_path, f"BO{tm_id[2:]}")
            push_repo(en_text_path, f"EN{tm_id[2:]}")
        logging.info(f"Done {tm_id}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="add missing segment to TMs")
    parser.add_argument(
        "tm_ids",
        nargs="+",
        type=str,
        help="list of TM ids",
    )
    parser.add_argument(
        "--no-push",
        action="store_true",
        help="Do not push to github",
    )

    args = parser.parse_args()

    run_pipeline(args)
