import requests
import time
import os
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}


# ─────────────────────────────
# 1. Helper to extract org slug
# ─────────────────────────────
def extract_org_name_from_url(url):
    if not url:
        return None
    parsed = urlparse(url)
    path_parts = [part for part in parsed.path.strip("/").split("/") if part]

    if not path_parts:
        return None

    host = parsed.netloc.lower()
    if "github.com" not in host:
        return path_parts[-1]

    if path_parts[0].lower() == "orgs" and len(path_parts) >= 2:
        return path_parts[1]

    return path_parts[0]


# ─────────────────────────────
# 2. Fetch organization repos
# ─────────────────────────────
def fetch_org_repos(org_name):
    """Fetch repositories of a GitHub organization."""
    url = f"https://api.github.com/orgs/{org_name}/repos?per_page=100&type=public"
    repos = []
    max_pages = 10  # Limit to prevent infinite loops
    page_count = 0
    while url and page_count < max_pages:
        page_count += 1
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            # Handle rate limiting
            if response.status_code == 403:
                print("WARNING: Rate limit reached. Sleeping for 60 seconds...")
                time.sleep(60)
                continue

            if response.status_code == 404:
                print(f"ERROR: Organization not found: {org_name}")
                return []

            if response.status_code != 200:
                print(f"ERROR: Failed to fetch repos for {org_name}: {response.status_code}")
                return []

            data = response.json()
            repos.extend(data)
            url = response.links.get("next", {}).get("url")
            time.sleep(1)
        except requests.exceptions.Timeout:
            print(f"WARNING: Timeout fetching repos for {org_name} (page {page_count})")
            break
        except requests.exceptions.RequestException as e:
            print(f"WARNING: Error fetching repos for {org_name}: {e}")
            break

    # Sort and keep only top 5 active repos
    repos = sorted(repos, key=lambda r: r.get("stargazers_count", 0), reverse=True)[:5]
    return repos


# ─────────────────────────────
# 3. Fetch PR data for repo
# ─────────────────────────────
def fetch_repo_pr_data(org_name, repo_name):
    """Fetch pull request data for a repository."""
    url = f"https://api.github.com/repos/{org_name}/{repo_name}/pulls?state=all&per_page=100"
    prs = []
    max_pages = 20  # Limit to prevent infinite loops
    page_count = 0
    while url and page_count < max_pages:
        page_count += 1
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 403:
                print("WARNING: Rate limit reached while fetching PRs. Sleeping 60s...")
                time.sleep(60)
                continue

            if response.status_code == 404:
                return []

            if response.status_code != 200:
                print(f"ERROR: Failed to fetch PRs for {org_name}/{repo_name}: {response.status_code}")
                return []

            data = response.json()
            prs.extend(data)
            url = response.links.get("next", {}).get("url")
            time.sleep(1)
        except requests.exceptions.Timeout:
            print(f"WARNING: Timeout fetching PRs for {org_name}/{repo_name} (page {page_count})")
            break
        except requests.exceptions.RequestException as e:
            print(f"WARNING: Error fetching PRs for {org_name}/{repo_name}: {e}")
            break
    return prs


# ─────────────────────────────
# 4. Compute metrics
# ─────────────────────────────
def calculate_metrics(repos):
    """Calculate total PRs, merged frequency, and activity score."""
    total_prs = 0
    merged_prs = 0

    for repo in repos:
        org_name = repo["owner"]["login"]
        repo_name = repo["name"]
        prs = fetch_repo_pr_data(org_name, repo_name)

        total_prs += len(prs)
        merged_prs += sum(1 for pr in prs if pr.get("merged_at"))

    merge_frequency = (merged_prs / total_prs) if total_prs > 0 else 0
    return {
        "total_prs": total_prs,
        "merged_prs": merged_prs,
        "merge_frequency": round(merge_frequency, 3)
    }
