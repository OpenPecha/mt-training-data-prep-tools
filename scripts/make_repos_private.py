import argparse
import os

import requests


def make_repos_private(repo_names, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.v3+json",
    }

    for repo_name in repo_names:
        url = f"https://api.github.com/repos/MonlamAI/{repo_name}"
        response = requests.patch(url, headers=headers, json={"private": True})

        if response.status_code == 200:
            print(f"{repo_name} is now private.")
        else:
            print(
                f"Failed to make {repo_name} private. Status code: {response.status_code}"
            )


def main():
    parser = argparse.ArgumentParser(description="Make GitHub repositories private.")
    parser.add_argument(
        "repos",
        metavar="repo_name",
        nargs="+",
        help="Repository names (space-separated)",
    )

    args = parser.parse_args()

    token = os.environ["GITHUB_TOKEN"]

    make_repos_private(args.repos, token)


if __name__ == "__main__":
    main()
