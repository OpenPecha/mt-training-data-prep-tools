import logging
import os
import subprocess
import time
from pathlib import Path
from typing import List, Optional

import requests
from git import Repo, cmd

GITHUB_USERNAME = os.environ["GITHUB_USERNAME"]
GITHUB_ACCESS_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_EMAIL = os.environ["GITHUB_EMAIL"]
GITHUB_ORG = os.environ["MAI_GITHUB_ORG"]
GITHUB_API_ENDPOINT = f"https://api.github.com/orgs/{GITHUB_ORG}/repos"

DEBUG = os.getenv("DEBUG", False)
quiet = "-q" if DEBUG else ""


def check_repo_exists(org, repo_name, access_token):
    url = f"https://api.github.com/repos/{org}/{repo_name}"
    headers = {
        "Authorization": f"token {access_token}",
        "Accept": "application/vnd.github.v3+json",
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return True
    elif response.status_code == 404:
        return False
    else:
        response.raise_for_status()


def create_github_repo_from_dir(repo_path: Path):
    logging.debug("Creating GitHub repo...")
    repo_name = repo_path.name

    # configure git users
    subprocess.run(f"git config --global user.name {GITHUB_USERNAME}".split())
    subprocess.run(f"git config --global user.email {GITHUB_EMAIL}".split())

    # Initialize a Git repository
    subprocess.run(f"git init {quiet}".split(), cwd=str(repo_path))

    # Commit the changes
    subprocess.run("git add . ".split(), cwd=str(repo_path))
    subprocess.run(
        f"git commit {quiet} -m".split() + ["Initial commit"], cwd=str(repo_path)
    )

    # Create a new repository on GitHub
    response = requests.post(
        GITHUB_API_ENDPOINT,
        json={
            "name": repo_name,
            "private": True,
        },
        auth=(GITHUB_USERNAME, GITHUB_ACCESS_TOKEN),
    )
    response.raise_for_status()

    time.sleep(3)

    # Add the GitHub remote to the local Git repository and push the changes
    remote_url = f"https://{GITHUB_ORG}:{GITHUB_ACCESS_TOKEN}@github.com/{GITHUB_ORG}/{repo_name}.git"
    subprocess.run(
        f"git remote add origin {remote_url}", cwd=str(repo_path), shell=True
    )
    # rename default branch to main
    subprocess.run("git branch -M main".split(), cwd=str(repo_path))
    subprocess.run(f"git push {quiet} -u origin main".split(), cwd=str(repo_path))

    return response.json()["html_url"]


def download_first_text_file_from_github_repo(
    repo_owner: str, repo_name: str, token: str, output_path: Path
) -> Optional[Path]:
    """Download text files from a GitHub repository.

    Args:
        repo_owner: The owner of the repository.
        repo_name: The name of the repository.
        token: The GitHub token.
        output_path: The output path to save the text files.

    Returns:
        output_fn(optionl[Path]): path to download text file if it exists.
    """
    repo_path = clone_or_pull_repo(repo_name, repo_owner, token, output_path)

    for text_fn in sorted(repo_path.glob("*.txt")):
        return text_fn
    return None


def commit_and_push(path: Path, msg: str, branch="main") -> None:
    """Commit and push local repo."""
    # configure git users
    subprocess.run(
        f"git config --global user.name {os.environ['GITHUB_USERNAME']}".split()
    )
    subprocess.run(
        f"git config --global user.email {os.environ['GITHUB_EMAIL']}".split()
    )
    repo = Repo(path)
    if branch in [branch.name for branch in repo.branches]:
        repo.git.checkout(branch)
    else:
        repo.git.checkout("-b", branch)
    repo.git.add(".", "--all")
    try:
        repo.git.commit("-m", msg)
        repo.git.push("-u", "origin", branch)
    except cmd.GitCommandError:
        return


def clone_or_pull_repo_form_url(repo_url: str, local_repo_path: Path) -> Path:
    """Clone or pull repo."""
    if local_repo_path.is_dir() and (local_repo_path / ".git").is_dir():
        repo = Repo(local_repo_path)
        repo.remotes.origin.pull()
    else:
        try:
            Repo.clone_from(repo_url, str(local_repo_path))
        except cmd.GitCommandError as e:
            print(e)
            raise ValueError(f"Repo({repo_url}) doesn't exist")
    return local_repo_path


def clone_or_pull_repo(repo: str, org: str, token: str, local_path: Path) -> Path:
    """Clone or pull repo."""
    repo_url = f"https://{token}@github.com/{org}/{repo}.git"
    local_path = clone_or_pull_repo_form_url(repo_url, local_path)
    return Path(local_path)


def download_monlanai_repo(repo: str, local_path: Path) -> Path:
    repo_path = clone_or_pull_repo(repo, GITHUB_ORG, GITHUB_ACCESS_TOKEN, local_path)
    return repo_path


def get_github_repos_with_prefix(
    org: str, token: str, prefix: str
) -> Optional[List[str]]:
    """Search all repo with matching name of `name_or_prefix` in `org`."""
    ...
    url = f"https://api.github.com/search/repositories?q=user:{org}+{prefix}in:name&sort=stars&order=desc"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        repos_json = response.json()
        return [repo["name"] for repo in repos_json["items"]]
    else:
        print(f"Request failed with status {response.status_code}")
        return []


if __name__ == "__main__":
    import tempfile

    print("downloading file...")
    with tempfile.TemporaryDirectory() as tmp_path:
        output_path = Path(tmp_path) / "text"
        output_path.mkdir(parents=True, exist_ok=True)
        repo_owner = "MonlamAI"
        repo_name = "BOtoh555_84000"
        token = os.environ["GITHUB_TOKEN"]
        downloaded_files = download_first_text_file_from_github_repo(
            repo_owner, repo_name, token, output_path
        )
        print(downloaded_files)
