# GitHub Branch Protection Report

This GitHub CLI extension fetches the repositories of a GitHub organization, gets the branch protection rules for each repository, gets the admins for each repository, and writes the data to a CSV file.

## Installation

1. Install it with the GitHub CLI
```
gh extension install https://github.com/homeles/gh-branch-protection-report.git
```

## Usage

1. Set your GitHub token and the name of the GitHub organization as environment variables in the .env file:

```
GITHUB_TOKEN=yourgithubtoken
ORG_NAME=yourorgname
```

2. Run the script:

```py
python3 gh-branch-protection-report --token yourgithubtoken --org yourorgname
```

Or
```bash
gh branch-protection-report --token yourgithubtoken --org yourorgname
```

The script will create a CSV file with the branch protection rules and admins for each repository in the specified GitHub organization. The CSV file includes the repository name, default branch, whether branch protection is enabled, the required review count, whether code owner reviews are required, whether restrictions are enabled, whether admin enforcement is enabled, whether deletions are allowed, whether linear history is required, and the admins of the repository.

Replace your `githubtoken` and `yourorgname` with your GitHub token and the name of the GitHub organization, respectively.