import argparse
import os

import requests


def add_to_publish_todo_repo(org, repo_name, file_path, access_token):
    base_url = f"https://api.github.com/repos/{org}/{repo_name}/contents/"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.v3+json",
    }

    url = base_url + file_path

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print(f"[INFO] '{file_path}' already added.")
        return

    payload = {"message": f"Add {file_path}", "content": ""}

    response = requests.put(url, headers=headers, json=payload)

    if response.status_code == 201:
        print(f"[INFO] '{file_path}' added to publish todo")
    else:
        print(f"[ERROR] Failed to add '{file_path}'.")
        print(f"[ERROR] Response: {response.text}")


def main():
    parser = argparse.ArgumentParser(description="Add Tms to publish todo")
    parser.add_argument("tms", nargs="+", help="List of TM ids")

    args = parser.parse_args()

    org = os.environ["MAI_GITHUB_ORG"]
    repo = os.environ["MAI_TMS_PUBLISH_TODO_REPO"]
    access_token = os.environ["GITHUB_TOKEN"]

    for tm in args.tms:
        add_to_publish_todo_repo(org, repo, tm, access_token)


if __name__ == "__main__":
    main()
