# app/scripts/generate_test_merge_dates.py
"""
Generate test merge dates based on merge_frequency from github_metrics table.
Creates realistic merge patterns for testing graph generation.
"""
import random
from datetime import datetime, timedelta, date
from sqlalchemy.exc import OperationalError
from app.common.database import SessionLocal
from app.models.github_metrics import GitHubMetrics
from app.models.merge_dates import MergeDate

def generate_merge_dates_for_org(org_slug, org_name, merge_frequency, days=30):
    """
    Generate random merge dates based on merge frequency.
    
    Args:
        org_slug: Organization slug
        org_name: Organization name
        merge_frequency: Merge frequency (0.0 to 1.0) - probability of merge per day
        days: Number of days to generate data for
    """
    merge_dates = []
    cutoff_date = datetime.utcnow().date() - timedelta(days=days)
    
    # Calculate expected merges per day
    # merge_frequency is a ratio, so we'll use it to determine daily merge probability
    # Higher frequency = more merges per day
    base_merges_per_day = merge_frequency * 10  # Scale it up (0.8 frequency = ~8 merges/day)
    
    current_date = cutoff_date
    while current_date <= datetime.utcnow().date():
        # Generate random number of merges for this day based on frequency
        # Use Poisson-like distribution centered around base_merges_per_day
        daily_merges = max(0, int(random.gauss(base_merges_per_day, base_merges_per_day * 0.5)))
        
        # Add some randomness - some days have more, some have less
        if random.random() < 0.1:  # 10% chance of a high-activity day
            daily_merges = int(daily_merges * random.uniform(1.5, 3.0))
        elif random.random() < 0.2:  # 20% chance of a low-activity day
            daily_merges = max(0, int(daily_merges * random.uniform(0.1, 0.5)))
        
        # Generate merge timestamps for this day
        for i in range(daily_merges):
            # Random time during the day
            hour = random.randint(0, 23)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            
            merged_at = datetime.combine(current_date, datetime.min.time().replace(
                hour=hour, minute=minute, second=second
            ))
            
            merge_dates.append({
                "merge_date": current_date,
                "merged_at": merged_at,
                "repository_name": f"repo-{random.randint(1, 5)}",  # Simulate multiple repos
                "pull_request_number": random.randint(1000, 9999)
            })
        
        current_date += timedelta(days=1)
    
    return merge_dates


def generate_test_merge_dates(days=30):
    """
    Generate test merge dates for all organizations in github_metrics table.
    """
    print(f"Generating test merge dates for last {days} days...")
    print("=" * 60)
    
    with SessionLocal() as session:
        # Get all organizations with merge_frequency
        orgs = session.query(
            GitHubMetrics.slug,
            GitHubMetrics.name,
            GitHubMetrics.merge_frequency
        ).filter(
            GitHubMetrics.merge_frequency.isnot(None),
            GitHubMetrics.merge_frequency > 0
        ).all()
    
    if not orgs:
        print("WARNING: No organizations with merge_frequency found in github_metrics.")
        return
    
    print(f"Found {len(orgs)} organizations with merge frequency data")
    print("=" * 60)
    
    total_merges = 0
    with SessionLocal() as session:
        for slug, name, frequency in orgs:
            try:
                print(f"  Generating merge dates for {name} ({slug}) - Frequency: {frequency:.3f}")
                
                # Generate merge dates
                merge_dates = generate_merge_dates_for_org(slug, name, frequency, days=days)
                
                if not merge_dates:
                    print(f"    WARNING: No merge dates generated")
                    continue
                
                # Store in database
                count = 0
                for md in merge_dates:
                    # Check if already exists
                    existing = session.query(MergeDate).filter(
                        MergeDate.organization_slug == slug,
                        MergeDate.merge_date == md["merge_date"],
                        MergeDate.pull_request_number == md["pull_request_number"],
                        MergeDate.repository_name == md["repository_name"]
                    ).first()
                    
                    if not existing:
                        merge_entry = MergeDate(
                            organization_slug=slug,
                            organization_name=name,
                            merge_date=md["merge_date"],
                            merged_at=md["merged_at"],
                            repository_name=md["repository_name"],
                            pull_request_number=md["pull_request_number"],
                            created_at=datetime.utcnow()
                        )
                        session.add(merge_entry)
                        count += 1
                
                try:
                    if count > 0:
                        session.commit()
                        print(f"    Stored {count} merge dates")
                        total_merges += count
                    else:
                        print(f"    WARNING: No new merge dates (may already exist)")
                except OperationalError as e:
                    print(f"    WARNING: Database error: {e}")
                    session.rollback()
                except Exception as e:
                    print(f"    ERROR: {e}")
                    session.rollback()
                    
            except Exception as e:
                print(f"  ERROR: Error processing {name}: {e}")
                continue
    
    print("=" * 60)
    print(f"Completed! Total merge dates stored: {total_merges}")
    print("=" * 60)


if __name__ == "__main__":
    import sys
    
    days = 30
    if len(sys.argv) > 1:
        try:
            days = int(sys.argv[1])
        except ValueError:
            pass
    
    generate_test_merge_dates(days=days)



