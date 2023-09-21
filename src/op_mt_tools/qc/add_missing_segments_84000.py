import logging
import re
from pathlib import Path

from diff_match_patch import diff_match_patch

from op_mt_tools import config
from op_mt_tools.github_utils import commit_and_push, download_monlanai_repo
from op_mt_tools.logger import setup_logger

logger_name = "qc.add_missing_segments"
logger_path = setup_logger(logger_name)

dmp = diff_match_patch()
dmp.Diff_Timeout = 0


def download_tm(tm_id):
    tm_path = config.TMS_PATH / tm_id
    tm_path = download_monlanai_repo(tm_id, tm_path)
    return tm_path


def get_tm_text(tm_path: Path, lang: str):
    text_fn = list(tm_path.glob(f"*-{lang.lower()}.txt"))[0]
    return text_fn.read_text(), text_fn


def get_src_text(tm_id: str, lang: str):
    repo_name = f"{lang.upper()}{tm_id[2:]}"
    repo_path = config.TEXTS_PATH / repo_name
    repo_path = download_monlanai_repo(repo_name, repo_path)
    src_text_fn = list(repo_path.glob("*.txt"))[0]
    return src_text_fn.read_text().replace("\n", " ")


def get_diff(text, src_text):
    text = text.strip()
    return dmp.diff_main(text, src_text)


def get_merged_text(diffs):
    text = ""
    for idx, diff in enumerate(diffs):
        if diff[0] == 1:
            if "\n" in diff[1]:
                text += diff[1]
        else:
            if idx == 0 and diff[0] == -1:
                text += diff[1] + " "
            else:
                text += diff[1]
    return text.strip()


def bo_remove_shad(text):
    return text.replace("།", "")


def common_cleanup(text):
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\{\{.*\}\}", "", text)
    text = re.sub(r"\s+$", "", text, flags=re.MULTILINE)
    return text


def bo_postprocess(text):
    text = text.replace("། ། ", "། །")
    text = text.replace("། །\n", "།\n།")
    text = common_cleanup(text)
    return text


def en_postprocess(text):
    text = common_cleanup(text)
    return text


def add_missing_segments(tm_path):
    tm_id = tm_path.name
    bo_text, bo_text_fn = get_tm_text(tm_path, "bo")
    bo_src_text = get_src_text(tm_id, "bo")
    en_text, en_text_fn = get_tm_text(tm_path, "en")
    en_src_text = get_src_text(tm_id, "en")

    bo_text_diffs = get_diff(bo_src_text, bo_remove_shad(bo_text))
    bo_merged_text = get_merged_text(bo_text_diffs)
    en_text_diffs = get_diff(en_src_text, en_text)
    en_merged_text = get_merged_text(en_text_diffs)
    if bo_merged_text.count("\n") != en_merged_text.count("\n"):
        logging.error(f"Segment does not match for {tm_id}")
        return

    bo_text_fn.write_text(bo_postprocess(bo_merged_text))
    en_text_fn.write_text(en_postprocess(en_merged_text))
    logging.info(f"Added missing segments for {tm_id}")


def run_pipeline(args):
    for tm_id in args.tm_ids:
        logging.info(f"Processing {tm_id}")
        try:
            tm_path = download_tm(tm_id)
        except Exception:
            logging.error(f"Failed to download {tm_id}")
            continue
        add_missing_segments(tm_path)

        if args.no_push:
            continue

        try:
            commit_and_push(tm_path, "Add missing segments")
            logging.info(f"Push {tm_id}")
        except Exception:
            logging.error(f"Error in pushing {tm_id}")


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
