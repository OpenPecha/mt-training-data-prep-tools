import argparse
import datetime
import os
import subprocess


def update_submodules(repo_path):
    # Update submodules
    os.chdir(repo_path)
    subprocess.run(["git", "submodule", "update", "--init", "--recursive"])


def create_release(current_date):
    # Create new release with tag of current date
    release_title = f"Release {current_date}"
    subprocess.run(
        [
            "gh",
            "release",
            "create",
            current_date,
            "--title",
            release_title,
            "--notes",
            "Automatic release created by script",
        ]
    )


def open_feedback_issue(current_date):
    # Open issue for users
    issue_title = f"Feedback for Release {current_date}"
    issue_body = "Please provide your feedback on the latest release. We would love to hear from you!"
    result = subprocess.run(
        [
            "gh",
            "issue",
            "create",
            "--title",
            issue_title,
            "--body",
            issue_body,
            "--json",
            "number",
        ],
        capture_output=True,
        text=True,
    )
    issue_number = result.stdout.strip()

    # Get release ID
    result = subprocess.run(
        ["gh", "release", "view", current_date, "--json", "id"],
        capture_output=True,
        text=True,
    )
    release_id = result.stdout.strip()

    # Link the issue in the release description
    result = subprocess.run(
        [
            "gh",
            "release",
            "edit",
            release_id,
            "--notes",
            f"$(gh release view {current_date} --json body --jq '.body' | sed 's/\"/\\\\\"/g')\\n\\nRelated: #{issue_number}'",  # noqa
        ],
        capture_output=True,
        text=True,
    )


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

    # Create new release or skip if specified
    if not args.no_release:
        current_date = datetime.date.today().strftime("%d.%m.%Y")
        create_release(current_date)
        open_feedback_issue(current_date)


if __name__ == "__main__":
    main()
