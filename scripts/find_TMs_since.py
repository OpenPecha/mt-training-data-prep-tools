import re
from datetime import datetime, timezone

import git


def get_commits_since_date(repo_path, since_date):
    repo = git.Repo(repo_path)
    commits = []

    for commit in repo.iter_commits():
        if commit.committed_datetime >= since_date:
            commits.append(commit.hexsha)

    return commits


def get_TM_id(diff_text):
    match = re.search(r"\+- (\bBO\w+)", diff_text)
    if match:
        bo_id = match.group(1)
        return f"TM{bo_id[2:]}"


repo_path = "C1A81F448"
since_date = datetime(2023, 4, 8, tzinfo=timezone.utc)
output_file = f"TM_created_since_{since_date.date()}.txt"

commits = get_commits_since_date(repo_path, since_date)

with open(output_file, "w") as f:
    for commit_sha in commits:
        repo = git.Repo(repo_path)
        commit = repo.commit(commit_sha)
        diff_text = repo.git.diff(commit.hexsha)
        TM_id = get_TM_id(diff_text)

        if not TM_id:
            continue

        print(TM_id, commit.committed_datetime)
        f.write(TM_id + " ")
