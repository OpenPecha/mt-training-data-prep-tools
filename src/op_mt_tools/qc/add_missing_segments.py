from pathlib import Path

from diff_match_patch import diff_match_patch

from op_mt_tools import config
from op_mt_tools.github_utils import download_monlanai_repo

dmp = diff_match_patch()
dmp.Diff_Timeout = 0


def get_tm_text(tm_path: Path, lang: str):
    text_fn = list(tm_path.glob(f"*-{lang.lower()}.txt"))[0]
    return text_fn.read_text()


def get_src_text(tm_id: str, lang: str):
    repo_name = f"{lang.upper()}{tm_id[2:]}"
    repo_path = config.TEXTS_PATH / repo_name
    repo_path = download_monlanai_repo(repo_name, repo_path)
    src_text_fn = list(repo_path.glob("*.txt"))[0]
    return src_text_fn.read_text()


def get_diff(text, src_text):
    text = text.strip()
    # text = text.replace("\n", "")
    return dmp.diff_main(text, src_text)


def print_missing(diffs):
    for diff in diffs:
        if diff[0] == 1:
            if diff[1] != "\n" and diff[1] != "།":
                print("Extra\n----------")
                print(diff[1])


def get_stats(diffs):
    stats = {
        "missing": 0,
        "common": 0,
        "extra": 0,
    }
    for diff in diffs:
        if diff[0] == 1:
            if diff[1] != "\n" and diff[1] != "།" and len(diff[1]) > 5:
                stats["extra"] += 1
        elif diff[0] == -1:
            if diff[1] != "\n" and diff[1] != "།" and len(diff[1]) > 5:
                stats["missing"] += 1
        else:
            if len(diff[1]) > 5:
                stats["common"] += 1

    return stats


def add_missing_segments(tm_path):
    tm_id = tm_path.name
    bo_text = get_tm_text(tm_path, "bo")
    bo_src_text = get_src_text(tm_id, "bo")
    en_text = get_tm_text(tm_path, "en")
    en_src_text = get_src_text(tm_id, "en")

    bo_text_diffs = get_diff(bo_text, bo_src_text)
    print(get_stats(bo_text_diffs))
    en_text_diffs = get_diff(en_text, en_src_text)
    print_missing(en_text_diffs)


def run_pipeline(path):
    for tm_path in path.iterdir():
        if not tm_path.is_dir():
            continue

        print("[INFO] Processing", tm_path.name)
        add_missing_segments(tm_path)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="add missing segment to TMs")
    parser.add_argument(
        "path",
        type=str,
        help="Path to TMs",
    )

    args = parser.parse_args()

    run_pipeline(Path(args.path))
