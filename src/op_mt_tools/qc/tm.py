import argparse
import os

import requests

qc_failed_tm_ids_fn = "TM_failed_qc.txt"


def get_github_file_contents(owner, repo, access_token, file_extension=".txt"):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    files = response.json()
    text_files = [
        file
        for file in files
        if file["type"] == "file" and file["name"].endswith(file_extension)
    ]
    return text_files


def check_text_file_lines(text_files, access_token):
    passed_text_files = 0
    for file in text_files:
        url = file["download_url"]
        response = requests.get(
            url, headers={"Authorization": f"Bearer {access_token}"}
        )
        response.raise_for_status()

        content = response.text
        lines = content.strip().split("\n")

        if len(lines) > 1:
            passed_text_files += 1

    return passed_text_files == len(text_files)


def log_failed_qc_tm_id(msg: str):
    print(msg)
    with open(qc_failed_tm_ids_fn, "a") as f:
        f.write(msg + "\n")


def qc_pipeline(tm_id: str):
    owner = "MonlamAI"
    access_token = os.environ["GITHUB_TOKEN"]

    try:
        text_files = get_github_file_contents(owner, tm_id, access_token)
    except requests.exceptions.HTTPError:
        msg = f"[QC Failed] TM_id: {tm_id}, TM not found"
        log_failed_qc_tm_id(msg)
        return

    if not check_text_file_lines(text_files, access_token):
        msg = f"[QC Failed] TM_id: {tm_id}, test: {check_text_file_lines.__name__}"
        log_failed_qc_tm_id(msg)


def run_qc(args):
    for tm_id in args.tm_ids:
        qc_pipeline(tm_id)


def main():
    parser = argparse.ArgumentParser(description="Check QC on TMs")

    parser.add_argument(
        "tm_ids",
        nargs="+",
        help="list of tm ids to QC",
    )

    args = parser.parse_args()

    run_qc(args)


if __name__ == "__main__":
    main()
