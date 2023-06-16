import argparse
import os

import requests


def transfer_repository(token, repo_name, current_org, new_org):
    url = f"https://api.github.com/repos/{current_org}/{repo_name}/transfer"

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }

    payload = {"owner": current_org, "new_owner": new_org, "repo": repo_name}

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        print(
            f"Successfully transferred repository '{repo_name}' from '{current_org}' to '{new_org}'."
        )

    except requests.HTTPError as e:
        print(
            f"Transfer failed with status code {e.response.status_code}: {e.response.text}"
        )

    except Exception as e:
        print(f"An error occurred: {e}")


# Usage
access_token = "<YOUR_ACCESS_TOKEN>"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Transfer ownership of a repository from one organization to another."
    )
    parser.add_argument(
        "--text_ids",
        nargs="+",
        help="add only these text",
    )

    args = parser.parse_args()

    token = os.environ["GITHUB_TOKEN"]
    from_org = "MonlamAI"
    to_org = "aspiration-ai"

    for text_id in args.text_ids:
        repo_name = f"TM{text_id}"
        print("Transfering repo: ", repo_name)
        transfer_repository(token, repo_name, from_org, to_org)
