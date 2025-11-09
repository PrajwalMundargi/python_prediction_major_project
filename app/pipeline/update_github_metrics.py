import time
import requests
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from sqlalchemy.exc import OperationalError
from app.common.database import SessionLocal
from app.models.github_metrics import GitHubMetrics
from app.models.historical_metrics import HistoricalMetrics
from app.pipeline.github_api import fetch_github_org_data
from app.pipeline.helper import get_organization_list
from datetime import datetime


def update_github_data(start_from_id=50):
    print("Running GitHub metrics updater...")
    if start_from_id:
        print(f"Starting from organization ID {start_from_id}")

    orgs = get_organization_list(start_from_id=start_from_id)  # load from DB instead of hardcoding
    print(f"Found {len(orgs)} organizations to process")
    
    # Double-check: filter out any orgs with ID < start_from_id (shouldn't happen, but safety check)
    if start_from_id:
        orgs = [org for org in orgs if org.get("id", 0) >= start_from_id]
        print(f"After final filter: {len(orgs)} organizations to process")
        if orgs:
            print(f"First organization ID: {orgs[0].get('id')}")

    for org in orgs:
        org_id = org.get("id", "?")
        display_name = org["display_name"]
        github_slug = org["github_slug"]
        print(f"Processing [{org_id}] {display_name} ({github_slug})...")

        # Fetch data with 10-minute timeout
        start_time = time.time()
        data = None
        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(fetch_github_org_data, github_slug)
                data = future.result(timeout=600)  # 10 minutes = 600 seconds
        except FuturesTimeoutError:
            elapsed = time.time() - start_time
            print(f"Timeout after {elapsed:.1f}s: Skipping {display_name} (took >10 minutes)")
            continue
        except Exception as e:
            print(f"ERROR: Error fetching data for {display_name}: {e}")
            continue

        if not data:
            print(f"WARNING: Skipping {display_name}, no data found.")
            continue

        retries = 3
        for attempt in range(retries):
            try:
                with SessionLocal() as session:
                    existing = session.query(GitHubMetrics).filter_by(slug=github_slug).first()

                    if existing:
                        # Update existing record
                        existing.name = display_name
                        existing.github_followers = data.get("followers")
                        existing.github_repos = data.get("public_repos")
                        existing.github_bio = data.get("bio")
                        existing.fetched_at = data.get("fetched_at")
                        existing.pull_requests = data.get("total_prs")
                        existing.merged_prs = data.get("merged_prs")
                        existing.merge_frequency = data.get("merge_frequency")
                    else:
                        # Create new record
                        new_entry = GitHubMetrics(
                            name=display_name,
                            slug=github_slug,
                            github_followers=data.get("followers"),
                            github_repos=data.get("public_repos"),
                            github_bio=data.get("bio"),
                            fetched_at=data.get("fetched_at"),
                            pull_requests=data.get("total_prs"),
                            merged_prs=data.get("merged_prs"),
                            merge_frequency=data.get("merge_frequency"),
                        )
                        session.add(new_entry)

                    # Store historical snapshot (before committing main update)
                    historical_entry = HistoricalMetrics(
                        organization_slug=github_slug,
                        organization_name=display_name,
                        merge_frequency=data.get("merge_frequency", 0.0),
                        total_prs=data.get("total_prs", 0),
                        merged_prs=data.get("merged_prs", 0),
                        recorded_at=datetime.utcnow()
                    )
                    session.add(historical_entry)
                    session.commit()  # Commit both updates together
                    
                    print(f"Updated {display_name}")
                    break  # success → exit retry loop

            except OperationalError as e:
                print(f"WARNING: Database connection lost during {display_name}: {e}")
                time.sleep(5)
                if attempt < retries - 1:
                    print("Retrying...")
                else:
                    print(f"ERROR: Failed to update {display_name} after retries.")
            except Exception as e:
                print(f"ERROR: Unexpected error for {display_name}: {e}")
                break

    print("All organizations processed.")

if __name__ == "__main__":
    import sys
    # When running as module: python -m app.pipeline.update_github_metrics 80
    # sys.argv will be: ['-m', 'app.pipeline.update_github_metrics', '80']
    # When running directly: python app/pipeline/update_github_metrics.py 80
    # sys.argv will be: ['app/pipeline/update_github_metrics.py', '80']
    
    print(f"Debug: sys.argv = {sys.argv}")
    
    # Find the first argument that looks like a number
    start_id = 50  # default
    for arg in sys.argv[1:]:
        try:
            start_id = int(arg)
            print(f"Debug: Found start_id = {start_id}")
            break
        except ValueError:
            continue
    
    print(f"Debug: Using start_id = {start_id}")
    update_github_data(start_from_id=start_id)
    print("Starting GitHub Metrics Updater Script...")
