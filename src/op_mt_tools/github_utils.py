import os
import subprocess
from pathlib import Path
from typing import List, Optional

import requests
from git import Repo, cmd


def download_first_text_file_from_github_repo(
    repo_owner: str, repo_name: str, token: str, output_path: Path, prefix: str = ""
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
    api_base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }

    # Get the list of files in the repository
    url = f"{api_base_url}/contents"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    files = response.json()

    # Filter the text files at the root level
    text_files = [
        file
        for file in files
        if file["type"] == "file"
        and file["path"].endswith(".txt")
        and file["name"].startswith(prefix)
    ]

    # Download each text file
    if text_files:
        text_file = text_files[0]
        raw_url = text_file["download_url"]
        response = requests.get(raw_url, headers=headers)
        response.raise_for_status()

        output_fn = output_path / f"{Path(text_file['name']).stem[:50]}.txt"
        output_fn.write_text(response.text)
        return output_fn
    return None


def commit_and_push(path: Path, msg: str) -> None:
    """Commit and push local repo."""
    # configure git users
    subprocess.run(
        f"git config --global user.name {os.environ['GITHUB_USERNAME']}".split()
    )
    subprocess.run(
        f"git config --global user.email {os.environ['GITHUB_EMAIL']}".split()
    )
    repo = Repo(path)
    repo.git.add(".", "--all")
    repo.git.commit("-m", msg)
    repo.remotes.origin.push()


def clone_or_pull_repo_form_url(repo_url: str, local_repo_path: Path) -> Path:
    """Clone or pull repo."""
    if local_repo_path.is_dir():
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
    return local_path


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
        repo_name = "EN0711"
        token = os.environ["GITHUB_TOKEN"]
        downloaded_files = download_first_text_file_from_github_repo(
            repo_owner, repo_name, token, output_path, prefix="[CLEANED]"
        )
        print(downloaded_files)
