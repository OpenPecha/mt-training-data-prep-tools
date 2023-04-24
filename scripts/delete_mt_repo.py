import os

from github import Github


def parse(raw_repos_to_delete):
    """get TM-test**** repos for deletion"""
    repos = []
    for line in raw_repos_to_delete.splitlines():
        if line.startswith("TM"):
            repos.append(line.split()[0])
    return repos


def input_multiline():
    """get input from user"""
    lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        lines.append(line)
    return "\n".join(lines)


if __name__ == "__main__":
    print("Enter the raw repos to delete: ")
    raw_repos_to_delete = input_multiline()
    repos_to_delete = parse(raw_repos_to_delete)

    g = Github(os.getenv("GITHUB_TOKEN"))
    org = g.get_organization(os.getenv("MAI_GITHUB_ORG"))
    for repo_to_delete in repos_to_delete:
        try:
            repo = org.get_repo(repo_to_delete)
            print("Deleting repo: ", repo.full_name)
            repo.delete()
        except Exception:
            print("Repo must be deleted already: ", repo_to_delete)
