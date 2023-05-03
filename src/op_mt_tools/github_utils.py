import os
from pathlib import Path
from typing import Optional

import requests


def download_frist_text_file_from_github_repo(
    repo_owner: str,
    repo_name: str,
    token: str,
    output_path: Path,
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
        if file["path"].endswith(".txt") and file["type"] == "file"
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


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as tmp_path:
        output_path = Path(tmp_path) / "text"
        output_path.mkdir(parents=True, exist_ok=True)
        repo_owner = "MonlamAI"
        repo_name = "BO0722"
        token = os.environ["GITHUB_TOKEN"]
        downloaded_files = download_frist_text_file_from_github_repo(
            repo_owner, repo_name, token, output_path
        )
        print(downloaded_files)
