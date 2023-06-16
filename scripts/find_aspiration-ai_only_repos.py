import json
import os

import requests

# Github API endpoint for getting all repos of an organization
url = "https://api.github.com/orgs/aspiration-ai/repos"

# Github API endpoint for getting a single repo of an organization
monlamai_url = "https://api.github.com/repos/MonlamAI/"

# Github API token for authentication
token = os.environ["GITHUB_TOKEN"]

# Headers for authentication
headers = {
    "Authorization": f"Token {token}",
    "Accept": "application/vnd.github.v3+json",
}

# List to store repo names that only exist on aspiration-ai org
aspiration_ai_only_repos = []

# Iterate through all pages of repos
while url:
    response = requests.get(url, headers=headers)
    repos = json.loads(response.text)

    # Iterate through each repo
    for repo in repos:
        # Check if the repo exists on MonlamAI org
        monlamai_response = requests.get(monlamai_url + repo["name"], headers=headers)
        if monlamai_response.status_code == 404:
            print("Found", repo["name"])
            aspiration_ai_only_repos.append(repo["name"])

    # Check if there is a next page of repos
    if "next" in response.links:
        url = response.links["next"]["url"]
    else:
        url = ""

# Write the repo names to a file
with open("aspiration-ai-only-repos.txt", "w") as f:
    for repo_name in aspiration_ai_only_repos:
        f.write(repo_name + "\n")
