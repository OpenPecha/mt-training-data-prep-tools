import os

from github import Github


def parse(raw_repos_to_delete):
    """get TM-test**** repos for deletion"""
    repos = []
    for line in raw_repos_to_delete.splitlines():
        # - BO0102: O8F4627FC
        text_id, pecha_id = line.split(":")
        text_id = text_id.strip().strip("- ")
        pecha_id = pecha_id.strip()
        tm_repo_id = f"TM{text_id[2:]}"
        repo = {
            "mai": tm_repo_id,
            "op": pecha_id,
        }
        repos.append(repo)
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
    mai_org = g.get_organization(os.getenv("MAI_GITHUB_ORG"))
    op_org = g.get_organization(os.getenv("OPENPECHA_DATA_GITHUB_ORG"))
    for repo_to_delete in repos_to_delete:
        try:
            for org, repo_name in repo_to_delete.items():
                print("Deleting repo: ", repo_name)
                if org == "mai":
                    repo = mai_org.get_repo(repo_to_delete["mai"])
                else:
                    repo = op_org.get_repo(repo_to_delete["op"])

                print("Deleting repo: ", repo.full_name)
                repo.delete()
        except Exception:
            print("Repo must be deleted already: ", repo_name)
