# check_merge_dates.py
"""Quick script to verify the organization_merge_dates table has data"""
from app.common.database import SessionLocal
from app.models.organization_merge_dates import OrganizationMergeDate
from sqlalchemy import func

with SessionLocal() as session:
    # Count total records
    total_count = session.query(func.count(OrganizationMergeDate.id)).scalar()
    print(f"Total merge dates stored: {total_count}")
    
    # Count by organization
    org_counts = session.query(
        OrganizationMergeDate.organization_name,
        func.count(OrganizationMergeDate.id).label('count')
    ).group_by(OrganizationMergeDate.organization_name).limit(10).all()
    
    print("\nSample organizations and their merge date counts:")
    print("=" * 60)
    for org_name, count in org_counts:
        print(f"  {org_name}: {count} merge dates")
    
    # Show a sample record
    sample = session.query(OrganizationMergeDate).first()
    if sample:
        print("\nSample record:")
        print("=" * 60)
        print(f"  Organization: {sample.organization_name} ({sample.organization_slug})")
        print(f"  Merge Date: {sample.merge_date}")
        print(f"  Merged At: {sample.merged_at}")
        print(f"  PR Number: {sample.pull_request_number}")
        print(f"  GitHub Followers: {sample.github_followers}")
        print(f"  GitHub Repos: {sample.github_repos}")
        print(f"  Merge Frequency: {sample.merge_frequency}")
        print(f"  Pull Requests: {sample.pull_requests}")
        print(f"  Merged PRs: {sample.merged_prs}")

