import argparse
import base64
import os

import requests

from op_mt_tools.tokenizers import find_splited_affix, fix_splited_affix


def get_file_content(owner, repo, file_path, access_token):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    content = response.json()["content"]
    decoded_content = base64.b64decode(content).decode("utf-8")

    return decoded_content


def update_file_content(owner, repo, file_path, new_content, access_token):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.v3+json",
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    file_data = response.json()
    sha = file_data["sha"]
    encoded_content = base64.b64encode(new_content.encode("utf-8")).decode("utf-8")

    data = {"message": "Update file content", "content": encoded_content, "sha": sha}

    response = requests.put(url, json=data, headers=headers)
    response.raise_for_status()

    print("File content updated successfully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fix splited affix for TM")
    parser.add_argument(
        "text_ids",
        nargs="+",
    )

    args = parser.parse_args()

    owner = "MonlamAI"
    token = os.environ["GITHUB_TOKEN"]

    for text_id in args.text_ids:
        print(f"Fixing splited affix for {text_id} ...")
        tm_id = f"TM{text_id}"
        file_path = f"{tm_id}-bo.txt"
        try:
            content = get_file_content(owner, tm_id, file_path, token)
        except Exception:
            print(f"Failed to get file content for {tm_id} {file_path}")
            continue
        if find_splited_affix(content):
            new_content = fix_splited_affix(content)
            update_file_content(owner, tm_id, file_path, new_content, token)
