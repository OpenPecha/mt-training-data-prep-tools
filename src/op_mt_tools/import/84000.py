import logging
import re
import shutil
from pathlib import Path

from .. import config
from ..github_utils import create_github_repo_from_dir
from ..logger import setup_logger

TM_SUFFIX = "84000"

logger_name = f"{Path(__file__).parent.name}.{Path(__file__).stem}"
logger_path = setup_logger(logger_name)


def get_text_pair_files(path: Path):
    bo_path = path / "bo"
    en_path = path / "en"
    for bo_text_fn in bo_path.glob("*.txt"):
        en_text_fn = en_path / bo_text_fn.name
        if not en_text_fn.exists():
            continue
        yield bo_text_fn, en_text_fn


def get_tm_id(fn: Path):
    return f"TM{fn.stem}_{TM_SUFFIX}"


def create_TM(bo_text_fn: Path, en_text_fn: Path):
    tm_id = get_tm_id(bo_text_fn)
    tm_path = config.TMS_PATH / tm_id
    tm_path.mkdir(parents=True, exist_ok=True)
    bo_text_fn_cp = tm_path / f"{tm_id}-bo.txt"
    en_text_fn_cp = tm_path / f"{tm_id}-en.txt"
    shutil.copyfile(str(bo_text_fn), str(bo_text_fn_cp))
    shutil.copyfile(str(en_text_fn), str(en_text_fn_cp))
    try:
        create_github_repo_from_dir(tm_path)
    except Exception as e:
        logging.error(f"Error in creating github repo {tm_id}")
        logging.error(e)
        return
    logging.info(f"Imported TM: {tm_id}")


def import_alignments(path: Path):
    for bo_text_fn, en_text_fn in get_text_pair_files(path):
        create_TM(bo_text_fn, en_text_fn)


def print_success_tms():
    logs = logger_path.read_text()
    pattern = r"Imported TM: (TM.*_84000)"
    tm_ids = re.findall(pattern, logs)
    for tm_id in tm_ids:
        print(tm_id)


def print_failed_tms():
    logs = logger_path.read_text()
    pattern = r"Error in creating github repo (TM.*_84000)"
    tm_ids = re.findall(pattern, logs)
    for tm_id in tm_ids:
        print(tm_id)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Import 84000 Alignment")
    parser.add_argument(
        "--path",
        type=str,
        help="Path to the 84000 alignment directory",
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
        import_alignments(Path(args.path))
    elif args.get_success_tms:
        print_success_tms()
    elif args.get_failed_tms:
        print_failed_tms()
    else:
        parser.print_help()
