from datetime import datetime
from app.services.github_service import fetch_org_repos, calculate_metrics
import requests

def fetch_github_org_data(org_name):
    """Fetch full org data including followers, repos, and PR metrics."""
    url = f"https://api.github.com/orgs/{org_name}"
    try:
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            print(f"⚠️ Failed to fetch data for {org_name} (status {response.status_code})")
            return None
    except requests.exceptions.Timeout:
        print(f"⚠️ Timeout fetching org data for {org_name}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error fetching org data for {org_name}: {e}")
        return None

    data = response.json()
    repos = fetch_org_repos(org_name)
    metrics = calculate_metrics(repos)

    return {
        "slug": org_name.lower(),
        "followers": data.get("followers"),
        "public_repos": data.get("public_repos"),
        "bio": data.get("description") or data.get("bio"),
        "fetched_at": datetime.utcnow(),
        "total_prs": metrics["total_prs"],
        "merged_prs": metrics["merged_prs"],
        "merge_frequency": metrics["merge_frequency"],
    }
