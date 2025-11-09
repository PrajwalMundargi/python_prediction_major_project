# test_generate_merge_dates.py
"""
Test file to generate random merge dates for 15 days for each organization
in github_metrics table. Dates are stored in organization_merge_dates table
along with organization information from github_metrics.
Uses merge_frequency from github_metrics to determine merge distribution.
"""
import random
from datetime import datetime, timedelta, date
from sqlalchemy.exc import OperationalError
from app.common.database import SessionLocal
from app.models.github_metrics import GitHubMetrics
from app.models.organization_merge_dates import OrganizationMergeDate


def generate_15_days_merge_dates(org_slug, org_name, merge_frequency):
    """
    Generate random merge dates with unpredictable patterns.
    Each entry gets a completely random merges_per_day value between 1-5.
    Dates are randomly distributed across a wide range.
    
    Args:
        org_slug: Organization slug
        org_name: Organization name
        merge_frequency: Merge frequency from github_metrics (0.0 to 1.0+) - not used for randomness
    
    Returns:
        List of merge date dictionaries with random merges_per_day (1-5) and random dates
    """
    merge_dates = []
    
    # Generate random dates within a wide range (last 15-60 days) for maximum variety
    today = datetime.utcnow().date()
    days_back = random.randint(15, 60)
    start_date = today - timedelta(days=days_back)
    
    # Generate 15 random merge entries (one per day concept, but dates are random)
    num_entries = 15
    
    # Generate unique random dates to avoid duplicates
    used_dates = set()
    
    for _ in range(num_entries):
        # Generate completely random date within the range, ensuring uniqueness
        attempts = 0
        while attempts < 100:  # Prevent infinite loop
            random_days_offset = random.randint(0, days_back)
            current_date = start_date + timedelta(days=random_days_offset)
            if current_date not in used_dates:
                used_dates.add(current_date)
                break
            attempts += 1
        else:
            # If we can't find unique date, just use any random date
            random_days_offset = random.randint(0, days_back)
            current_date = start_date + timedelta(days=random_days_offset)
        
        # Each entry gets a completely random merges_per_day value between 1-5
        # This ensures every entry has a different random value
        merges_per_day = random.randint(1, 5)
        
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
            "merges_per_day": merges_per_day  # Random value between 1-5, different for each entry
        })
    
    # Sort by date for better organization
    merge_dates.sort(key=lambda x: x["merge_date"])
    
    return merge_dates


def generate_test_merge_dates_15_days():
    """
    Generate exactly 15 days of merge dates for all organizations in github_metrics table.
    Stores dates in organization_merge_dates table along with organization information.
    """
    print("Generating 15 days of merge dates for all organizations...")
    print("=" * 60)
    
    with SessionLocal() as session:
        # Get all organizations with their full information from github_metrics
        orgs = session.query(GitHubMetrics).all()
    
    if not orgs:
        print("WARNING: No organizations found in github_metrics table.")
        return
    
    print(f"Found {len(orgs)} organizations to process")
    print("=" * 60)
    
    total_merges = 0
    with SessionLocal() as session:
        for org in orgs:
            try:
                # Use merge_frequency if available, otherwise default to 0.5
                merge_freq = org.merge_frequency if org.merge_frequency is not None and org.merge_frequency > 0 else 0.5
                
                print(f"  Generating 15 days of merge dates for {org.name} ({org.slug})")
                print(f"      Merge frequency: {merge_freq:.3f}")
                
                # Generate exactly 15 days of merge dates
                merge_dates = generate_15_days_merge_dates(org.slug, org.name, merge_freq)
                
                if not merge_dates:
                    print(f"    WARNING: No merge dates generated")
                    continue
                
                print(f"    Generated {len(merge_dates)} merge dates across 15 days")
                
                # Store in database with organization information
                count = 0
                for md in merge_dates:
                    # Check if this exact merge date already exists
                    existing = session.query(OrganizationMergeDate).filter(
                        OrganizationMergeDate.organization_slug == org.slug,
                        OrganizationMergeDate.merge_date == md["merge_date"],
                        OrganizationMergeDate.merged_at == md["merged_at"]
                    ).first()
                    
                    if not existing:
                        merge_entry = OrganizationMergeDate(
                            # Organization identification
                            organization_slug=org.slug,
                            organization_name=org.name,
                            
                            # Merge date information
                            merge_date=md["merge_date"],
                            merged_at=md["merged_at"],
                            merges_per_day=md.get("merges_per_day", 0),  # Number of merges on this day
                            
                            # Organization information from github_metrics
                            fetched_at=org.fetched_at,
                            
                            # Metadata
                            created_at=datetime.utcnow()
                        )
                        session.add(merge_entry)
                        count += 1
                
                try:
                    if count > 0:
                        session.commit()
                        print(f"    Stored {count} new merge dates with organization information")
                        total_merges += count
                    else:
                        print(f"    WARNING: No new merge dates (may already exist)")
                except OperationalError as e:
                    print(f"    WARNING: Database error: {e}")
                    session.rollback()
                except Exception as e:
                    print(f"    ERROR: {e}")
                    import traceback
                    traceback.print_exc()
                    session.rollback()
                    
            except Exception as e:
                print(f"  ERROR: Error processing {org.name}: {e}")
                import traceback
                traceback.print_exc()
                continue
    
    print("=" * 60)
    print(f"Completed! Total merge dates stored: {total_merges}")
    print("=" * 60)


if __name__ == "__main__":
    generate_test_merge_dates_15_days()

