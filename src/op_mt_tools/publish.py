import argparse
import logging
import os
import subprocess
from pathlib import Path
from typing import List

from .logger import setup_logger

log_fn = setup_logger(Path(__file__).name)

GITHUB_ORG = os.environ["MAI_GITHUB_ORG"]


def commit_and_push_changes(repo_path, msg):
    # Commit and push submodule changes
    os.chdir(repo_path)
    subprocess.run(["git", "add", "--all"])
    subprocess.run(["git", "commit", "-m", msg])
    subprocess.run(["git", "push"])


def get_tm_github_url(tm_id: str):
    tm_url = f"https://github.com/{GITHUB_ORG}/{tm_id}.git"
    return tm_url


def add_submodule(submodule_path: str, submodule_url: str, repo_path: str):
    """Export TM as submodules of `output_dir`."""
    result = subprocess.run(
        [
            "git",
            "submodule",
            "add",
            "-b",
            "main",
            "--force",
            submodule_url,
            submodule_path,
        ],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr)


def update_submodules(repo_path):
    # Update submodules
    os.chdir(repo_path)
    print("[INFO] Pulling latest changes...")
    subprocess.run(["git", "pull"])
    print("[INFO] Updating TMs...")
    subprocess.run(["git", "submodule", "update", "--init", "--remote", "--recursive"])


def add_TM(
    dataset_path: Path,
    tm_id: str,
    tms_path: str = "data",
):
    """Add TM to dataset."""
    dataset_path = Path(dataset_path).resolve()
    tm_path = dataset_path / tms_path / tm_id
    if tm_path.exists():
        logging.debug(f"TM: {tm_id} already exists in {dataset_path.name}")
        return

    try:
        tm_github_url = get_tm_github_url(tm_id)
        tm_relative_path = f"{tms_path}/{tm_id}"
        add_submodule(tm_relative_path, tm_github_url, str(dataset_path))
    except Exception as e:
        logging.error(f"{tm_id} Failed to add to {dataset_path.name}: {e}")

        return

    logging.info(f"{tm_id} added to {dataset_path.name}")


def add_tms_to_dataset(dataset_path: Path, tm_ids: List[str]):
    for tm_id in tm_ids:
        add_TM(dataset_path, tm_id)
    commit_and_push_changes(dataset_path, "Add TMs")


def print_success_tms():
    for line in log_fn.read_text().splitlines():
        if "- INFO -" in line:
            print(line.split(" ")[0])


def print_failed_tms():
    for line in log_fn.read_text().splitlines():
        if "- ERROR -" in line:
            print(line.split(" ")[0])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Add TMs to dataset or update existing TMs"
    )
    parser.add_argument("dataset_path", help="TMs repo path")
    parser.add_argument(
        "--tm_ids",
        nargs="+",
        help="TM ids to be added",
    )
    parser.add_argument(
        "--update_tms",
        action="store_true",
        help="whether to update tms",
    )
    args = parser.parse_args()

    add_tms_to_dataset(Path(args.dataset_path), args.tm_ids)

    if args.update_tms:
        update_submodules(args.dataset_path)
