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
        last_commit = repo.head.commit

        if "QC" in last_commit.message:
            branch_name = "qc-review"

            if branch_name not in [branch.name for branch in repo.branches]:
                repo.git.checkout("-b", branch_name)
            repo.git.push("-u", "origin", branch_name)

            # Remove the last commit from main and force push
            main_branch = repo.heads.main  # Change to the appropriate main branch name
            repo.git.checkout("main")
            repo.git.reset("--hard", "HEAD~1")
            repo.git.push("--force", "origin", main_branch)
            print(f"{repo_path.name}: removed last commit from main branch")
