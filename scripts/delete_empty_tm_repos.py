import argparse
import os

import requests

# Read the GitHub token from the environment variable
token = os.environ.get("GITHUB_TOKEN")

# Set the headers for the API requests
headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json",
}

# Define the URL for the API requests
url = "https://api.github.com/repos/aspiration-ai/"


def delete_empty_repo(repo_name):
    response = requests.get(url + f"{repo_name}", headers=headers)
    repo = response.json()
    print("deleting ", repo_name)
    if "size" in repo and repo["size"] == 0:
        payload = {"owner": "aspiration-ai", "repo": repo_name}
        response = requests.delete(url + f"{repo_name}", headers=headers, json=payload)
        if response.status_code == 204:
            print(f"{repo_name} deleted successfully")
        else:
            print(f"Error deleting {repo_name}: {response.status_code}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Transfer ownership of a repository from one organization to another."
    )
    parser.add_argument(
        "text_ids",
        nargs="+",
        help="add only these text",
    )

    args = parser.parse_args()

    for tm in args.text_ids:
        repo_name = f"TM{tm}"
        delete_empty_repo(repo_name)
