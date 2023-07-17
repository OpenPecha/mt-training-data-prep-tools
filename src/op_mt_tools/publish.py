import argparse
import datetime
import os
import random
import string
import subprocess
import time
from pathlib import Path


def commit_and_push_changes(repo_path, msg):
    # Commit and push submodule changes
    os.chdir(repo_path)
    print("[INFO] Committing and pushing changes...")
    subprocess.run(["git", "add", "--all"])
    subprocess.run(["git", "commit", "-m", msg])
    subprocess.run(["git", "push"])


def get_TMs_ids(repo_path: Path):
    """Get all latest TMs."""
    os.chdir(repo_path)
    subprocess.run(["git", "pull"])
    for path in Path(repo_path).iterdir():
        if path.name == "README.md":
            continue
        yield path.name


def export_TM(tm: str, export_dir: Path, branch):
    """Export TM as submodules of `output_dir`."""
    tm_url = f"https://github.com/{os.environ['MAI_GITHUB_ORG']}/{tm}.git"
    subprocess.run(
        ["git", "submodule", "add", "-b", branch, "--force", tm_url], cwd=export_dir
    )


def add_TMs(
    tms_repo_path: Path,
    publish_todo_repo_path: Path,
    branch: str = "main",
):
    """Export all latest TMs."""
    print("[INFO] Adding New TMs ...")
    tm_ids = get_TMs_ids(publish_todo_repo_path)

    if not tm_ids:
        print("[INFO] No TM found. Exiting...")
        return

    for tm_id in tm_ids:
        if not tm_id:
            continue
        if tms_repo_path.joinpath(tm_id).exists():
            print(f"[INFO] {tm_id} already exists. Skipping...")
            continue
        export_TM(tm_id, tms_repo_path, branch)

    msg = "add TMs on " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    commit_and_push_changes(tms_repo_path, msg)
    print("[INFO] Exporting all TMs done!")


def update_submodules(repo_path):
    # Update submodules
    os.chdir(repo_path)
    print("[INFO] Pulling latest changes...")
    subprocess.run(["git", "pull"])
    print("[INFO] Updating TMs...")
    subprocess.run(["git", "submodule", "update", "--init", "--remote", "--recursive"])


def create_release(version):
    # Create new release with tag of current date
    print("[INFO] Creating new release...")
    release_title = f"Release {version}"
    subprocess.run(
        [
            "gh",
            "release",
            "create",
            f"{version}",
            "--title",
            release_title,
            "--notes",
            f"Please provide your feekback on this new release in the issue titled `{version} Feedback`",  # noqa
        ]
    )


def open_feedback_issue(version):
    # Open issue for users
    issue_title = f"{version} Feedback"
    issue_body = f"Please provide your feedback on the release {version}. We would love to hear from you!"
    subprocess.run(
        [
            "gh",
            "issue",
            "create",
            "--title",
            issue_title,
            "--body",
            issue_body,
            "--label",
            "feedback",
        ],
    )


def generate_release_tag():
    # Generate release tag with random two-character alphabets
    current_date = datetime.date.today().strftime("%d.%m.%Y")
    random_chars = "".join(random.choices(string.ascii_lowercase, k=2))
    release_tag = f"{current_date}-{random_chars}"
    return release_tag


def main():
    parser = argparse.ArgumentParser(
        description="Update submodules, create release, and open issue for a repository"
    )
    parser.add_argument("tms_repo_path", help="TMs repo path")
    parser.add_argument("publish_todo_path", help="Publish TODO repo path")
    parser.add_argument(
        "--no-release", action="store_true", help="Skip creating a new release"
    )
    args = parser.parse_args()

    # Update submodules
    add_TMs(Path(args.tms_repo_path), Path(args.publish_todo_path))
    update_submodules(args.tms_repo_path)
    commit_and_push_changes(args.tms_repo_path, "update TMs")

    # Create new release or skip if specified
    if not args.no_release:
        release_tag = generate_release_tag()
        create_release(release_tag)
        open_feedback_issue(release_tag)


if __name__ == "__main__":
    main()
