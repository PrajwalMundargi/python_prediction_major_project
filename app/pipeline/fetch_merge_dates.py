# app/pipeline/fetch_merge_dates.py
"""
Fetch merge dates from GitHub API for organizations in github_metrics table.
Stores merge dates for the last 30 days.
"""
import requests
import time
from datetime import datetime, timedelta, timezone
from sqlalchemy.exc import OperationalError
from app.common.database import SessionLocal
from app.models.github_metrics import GitHubMetrics
from app.models.merge_dates import MergeDate
from app.services.github_service import fetch_org_repos, headers
import os
from dotenv import load_dotenv

load_dotenv()

def fetch_merged_prs_for_repo(org_name, repo_name, days=30):
    """
    Fetch merged pull requests for a repository within the last N days.
    
    Args:
        org_name: Organization name
        repo_name: Repository name
        days: Number of days to look back
    
    Returns:
        List of merged PR data
    """
    merged_prs = []
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Use state=all to get both open and closed PRs, then filter for merged
    url = f"https://api.github.com/repos/{org_name}/{repo_name}/pulls?state=all&per_page=100&sort=updated"
    page = 1
    max_pages = 10
    
    while page <= max_pages:
        try:
            response = requests.get(f"{url}&page={page}", headers=headers, timeout=30)
            
            if response.status_code == 403:
                print("WARNING: Rate limit reached. Sleeping for 60 seconds...")
                time.sleep(60)
                continue
            
            if response.status_code == 404:
                return []
            
            if response.status_code != 200:
                print(f"WARNING: Failed to fetch PRs for {org_name}/{repo_name}: {response.status_code}")
                return []
            
            prs = response.json()
            if not prs:
                break
            
            # Debug: Check what we're getting
            closed_count = len(prs)
            merged_count = sum(1 for pr in prs if pr.get("merged_at"))
            
            for pr in prs:
                # Only include merged PRs
                if pr.get("merged_at"):
                    try:
                        merged_at_str = pr["merged_at"].replace("Z", "+00:00")
                        merged_at = datetime.fromisoformat(merged_at_str)
                        # Ensure timezone-aware
                        if merged_at.tzinfo is None:
                            merged_at = merged_at.replace(tzinfo=timezone.utc)
                        # Make cutoff_date timezone-aware for comparison
                        cutoff_aware = cutoff_date
                        if cutoff_aware.tzinfo is None:
                            cutoff_aware = cutoff_aware.replace(tzinfo=timezone.utc)
                        # Only include PRs merged within the date range
                        if merged_at >= cutoff_aware:
                            merged_prs.append({
                                "merged_at": merged_at,
                                "number": pr.get("number"),
                                "title": pr.get("title"),
                                "repo": repo_name
                            })
                        else:
                            # If we've gone past the date range, stop
                            return merged_prs
                    except Exception as e:
                        print(f"    WARNING: Error processing PR #{pr.get('number')}: {e}")
                        continue
            
            # Check if there are more pages
            if "next" not in response.links:
                break
            
            page += 1
            time.sleep(1)  # Rate limiting
            
        except requests.exceptions.Timeout:
            print(f"WARNING: Timeout fetching PRs for {org_name}/{repo_name}")
            break
        except Exception as e:
            print(f"WARNING: Error fetching PRs for {org_name}/{repo_name}: {e}")
            break
    
    return merged_prs


def fetch_merge_dates_for_organization(org_slug, org_name, days=30):
    """
    Fetch merge dates for an organization by checking its repositories.
    
    Args:
        org_slug: Organization slug
        org_name: Organization name
        days: Number of days to look back
    """
    print(f"  Fetching merge dates for {org_name} ({org_slug})...")
    
    # Get repositories for this organization
    repos = fetch_org_repos(org_slug)
    
    if not repos:
        print(f"  WARNING: No repositories found for {org_slug}")
        return 0
    
    # Limit to top 5 repos to avoid too many API calls
    repos = repos[:5]
    
    all_merged_prs = []
    for repo in repos:
        repo_name = repo["name"]
        try:
            merged_prs = fetch_merged_prs_for_repo(org_slug, repo_name, days=days)
            if merged_prs:
                print(f"    Found {len(merged_prs)} merged PRs in {repo_name}")
            else:
                print(f"    WARNING: No merged PRs found in {repo_name}")
            all_merged_prs.extend(merged_prs)
        except Exception as e:
            print(f"    ERROR: Error fetching PRs from {repo_name}: {e}")
            continue
        time.sleep(1)  # Rate limiting between repos
    
    if not all_merged_prs:
        print(f"  WARNING: No merged PRs found for {org_name} in last {days} days")
        return 0
    
    print(f"  Total merged PRs found: {len(all_merged_prs)}")
    
    # Store merge dates in database
    with SessionLocal() as session:
        count = 0
        for pr in all_merged_prs:
            merge_date = pr["merged_at"].date()
            
            # Check if this merge date already exists for this org
            existing = session.query(MergeDate).filter(
                MergeDate.organization_slug == org_slug,
                MergeDate.merge_date == merge_date,
                MergeDate.pull_request_number == pr["number"],
                MergeDate.repository_name == pr["repo"]
            ).first()
            
            if not existing:
                merge_date_entry = MergeDate(
                    organization_slug=org_slug,
                    organization_name=org_name,
                    merge_date=merge_date,
                    merged_at=pr["merged_at"],
                    repository_name=pr["repo"],
                    pull_request_number=pr["number"],
                    created_at=datetime.utcnow()
                )
                session.add(merge_date_entry)
                count += 1
        
        try:
            if count > 0:
                session.commit()
                print(f"  Stored {count} merge dates for {org_name}")
            else:
                print(f"  WARNING: No new merge dates to store for {org_name} (may already exist)")
            return count
        except OperationalError as e:
            print(f"  WARNING: Database error for {org_name}: {e}")
            session.rollback()
            return 0
        except Exception as e:
            print(f"  ERROR: Error saving merge dates for {org_name}: {e}")
            import traceback
            traceback.print_exc()
            session.rollback()
            return 0


def fetch_all_merge_dates(days=30, start_from_id=None):
    """
    Fetch merge dates for all organizations in github_metrics table.
    
    Args:
        days: Number of days to look back (default: 30)
        start_from_id: Optional organization ID to start from
    """
    print(f"Fetching merge dates for last {days} days...")
    print("=" * 60)
    
    with SessionLocal() as session:
        query = session.query(GitHubMetrics.slug, GitHubMetrics.name)
        
        if start_from_id:
            query = query.filter(GitHubMetrics.id >= start_from_id)
        
        orgs = query.all()
    
    if not orgs:
        print("WARNING: No organizations found in github_metrics table.")
        return
    
    print(f"Found {len(orgs)} organizations to process")
    print("=" * 60)
    
    total_merges = 0
    for slug, name in orgs:
        try:
            count = fetch_merge_dates_for_organization(slug, name, days=days)
            total_merges += count
        except Exception as e:
            print(f"  ERROR: Error processing {name}: {e}")
            continue
    
    print("=" * 60)
    print(f"Completed! Total merge dates stored: {total_merges}")
    print("=" * 60)


if __name__ == "__main__":
    import sys
    
    days = 30
    start_id = None
    
    if len(sys.argv) > 1:
        try:
            days = int(sys.argv[1])
        except ValueError:
            pass
    
    if len(sys.argv) > 2:
        try:
            start_id = int(sys.argv[2])
        except ValueError:
            pass
    
    fetch_all_merge_dates(days=days, start_from_id=start_id)

