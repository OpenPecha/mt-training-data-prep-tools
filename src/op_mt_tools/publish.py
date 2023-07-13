import argparse
import datetime
import os
import random
import string
import subprocess


def update_submodules(repo_path):
    # Update submodules
    os.chdir(repo_path)
    subprocess.run(["git", "pull"])
    subprocess.run(["git", "submodule", "update", "--init", "--remote", "--recursive"])


def commit_and_push_changes(repo_path):
    # Commit and push submodule changes
    os.chdir(repo_path)
    subprocess.run(["git", "commit", "-am", "Update TMs"])
    subprocess.run(["git", "push"])


def create_release(version):
    # Create new release with tag of current date
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
    parser.add_argument("repo_path", help="Repository path")
    parser.add_argument(
        "--no-release", action="store_true", help="Skip creating a new release"
    )
    args = parser.parse_args()

    # Update submodules
    update_submodules(args.repo_path)
    commit_and_push_changes(args.repo_path)

    # Create new release or skip if specified
    if not args.no_release:
        release_tag = generate_release_tag()
        create_release(release_tag)
        open_feedback_issue(release_tag)


if __name__ == "__main__":
    main()
