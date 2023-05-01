import os
from pathlib import Path

import requests


def download_text_files_from_github_repo(
    repo_owner: str,
    repo_name: str,
    token: str,
    output_path: Path,
) -> Path:
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
    for text_file in text_files:
        raw_url = text_file["download_url"]
        response = requests.get(raw_url, headers=headers)
        response.raise_for_status()

        output_fn = output_path / f"{Path(text_file['name']).stem[:200]}.txt"
        output_fn.write_text(response.text)

    return output_path


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as tmp_path:
        output_path = Path(tmp_path) / "text"
        output_path.mkdir(parents=True, exist_ok=True)
        repo_owner = "MonlamAI"
        repo_name = "BO0722"
        token = os.environ["GITHUB_TOKEN"]
        downloaded_files = download_text_files_from_github_repo(
            repo_owner, repo_name, token, output_path
        )

        assert len(list(downloaded_files.iterdir())) == 1
