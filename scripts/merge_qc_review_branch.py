import sys
from pathlib import Path

import git

if __name__ == "__main__":
    tms_path = Path(sys.argv[1])
    assert tms_path.exists(), f"{tms_path} does not exist."

    for repo_path in tms_path.iterdir():
        if not (Path(repo_path) / ".git").exists():
            continue

        repo = git.Repo(repo_path)
        repo.git.checkout("main")
        branch_name = "qc-review"

        if branch_name in [branch.name for branch in repo.branches]:
            repo.git.merge(branch_name)
            # Remove the last commit from main and force push
            repo.git.push("origin", "main")
            print(f"{repo_path.name}: merged {branch_name} into main")
