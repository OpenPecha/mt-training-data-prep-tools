import os

import requests


def check_private_repo_existence(owner, repo_name, access_token):
    url = f"https://api.github.com/repos/{owner}/{repo_name}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.v3+json",
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return True
    elif response.status_code == 404:
        return False
    else:
        print(f"Error: {response.status_code}")
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Check if TM exists")
    parser.add_argument(
        "tm_ids",
        type=str,
        nargs="+",
    )

    args = parser.parse_args()
    owner = os.environ["MAI_GITHUB_ORG"]
    access_token = os.environ["GITHUB_TOKEN"]

    for tm_id in args.tm_ids:
        exists = check_private_repo_existence(owner, tm_id, access_token)
        if not exists:
            print(f"{tm_id} exists: {exists}")
