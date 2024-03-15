#!/usr/bin/env python3

import argparse
import os
import requests
import csv
import datetime
import time
from dotenv import load_dotenv

load_dotenv()

parser = argparse.ArgumentParser(description='Get GitHub branch protection report.')
parser.add_argument('--token', help='GitHub token')
parser.add_argument('--orgName', help='GitHub organization name')
args = parser.parse_args()

github_token = args.token or os.getenv('GITHUB_TOKEN')
org_name = args.orgName or os.getenv('ORG_NAME')

# rest of your code
headers = {
    'Authorization': f'token {github_token}'
}


def make_request(url):
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code != 403:
            response.raise_for_status()
            return response.json()
        reset_time = int(response.headers['X-RateLimit-Reset'])
        sleep_time = reset_time - time.time()
        if sleep_time > 0:
            time.sleep(sleep_time)

def get_repos(org_name):
    repos = []
    page = 1
    while True:
        current_page_repos = make_request(f'https://api.github.com/orgs/{org_name}/repos?per_page=100&page={page}')
        if not current_page_repos:
            break
        repos.extend(current_page_repos)
        page += 1
    return repos

def get_branch_protection_rules(repo):
    try:
        rule = make_request(f'https://api.github.com/repos/{org_name}/{repo["name"]}/branches/{repo["default_branch"]}/protection')
        return {
            'enabled': True,
            'required_pull_request_reviews_count': rule.get('required_pull_request_reviews', {}).get('required_approving_review_count', None),
            'require_code_owner_reviews': rule.get('required_pull_request_reviews', {}).get('require_code_owner_reviews', None),
            'enforce_admins': rule.get('enforce_admins', {}).get('enabled', None),
            'restrictions': True if rule.get('restrictions') else False,
            'allow_deletions': rule.get('allow_deletions', {}).get('enabled', None),
            'allow_force_pushes': rule.get('allow_force_pushes', {}).get('enabled', None),
            'required_conversation_resolution': rule.get('required_conversation_resolution', {}).get('enabled', None),
            'require_last_push_approval': rule.get('required_pull_request_reviews', {}).get('require_last_push_approval', None),
            'required_status_checks': True if rule.get('required_status_checks') else False,
            'lock_branch': rule.get('lock_branch', {}).get('enabled', None),
            'allow_fork_syncing': rule.get('allow_fork_syncing', {}).get('enabled', None),
            'required_linear_history': rule.get('required_linear_history', {}).get('enabled', None),
            
        }
    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 404:
            return {
                'enabled': False,
                'required_pull_request_reviews_count': None,
                'require_code_owner_reviews': None,
                'enforce_admins': None,
                'restrictions': None,
                'allow_deletions': None,
                'allow_force_pushes': None,
                'required_conversation_resolution': None,
                'require_last_push_approval': None,
                'required_status_checks': None,
                'lock_branch': None,
                'allow_fork_syncing': None,
                'required_linear_history': None
            }
        else:
            raise

def get_repo_admins(repo):
    admins = make_request(f'https://api.github.com/repos/{org_name}/{repo["name"]}/collaborators?permission=admin')
    return '; '.join(user['login'] for user in admins)


def main():
    if not github_token or not org_name:
        print('Error: Missing required parameters.')
        print('Usage: python gh-branch-protection-report.py --token <githubToken> --orgName <orgName>')
        print('Or set the GITHUB_TOKEN and ORG_NAME environment variables.')
        exit(1)

    try:
        requests.get('https://api.github.com/user', headers=headers).raise_for_status()
    except requests.exceptions.HTTPError as err:
        print('Error: Invalid GitHub token.')
        exit(1)

    try:
        requests.get(f'https://api.github.com/orgs/{org_name}', headers=headers).raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(f'Error: The organization {org_name} does not exist.')
        exit(1)

    repos = get_repos(org_name)
    print(f'Total Repos: {len(repos)}')

    date = datetime.datetime.now()
    date_string = date.strftime('%Y-%m-%d')
    time_string = date.strftime('%H:%M:%S')
    file_name = f'{org_name}-{date_string}_{time_string}-branch-protection-report.csv'

    with open(file_name, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['repo', 'branch', 'enabled', 'Review Count', 'require code owners', 'restrictions', 'enforce admins', 'allow deletions', 'require linear history', 'admins'])
        file.flush()

        for repo in repos:
            rule = get_branch_protection_rules(repo)
            admins = get_repo_admins(repo)
            print(f"Repo: {repo['name']}, Branch: {repo['default_branch']}, Enabled: {rule['enabled']}")
            writer.writerow(
                [
                    repo['name'],
                    repo['default_branch'],
                    rule['enabled'],
                    rule['required_pull_request_reviews_count'],
                    rule['require_code_owner_reviews'],
                    rule['restrictions'],
                    rule['enforce_admins'],
                    rule['allow_deletions'],
                    rule['required_linear_history'],
                    admins
                ]
            )
            file.flush()

if __name__ == '__main__':
    main()