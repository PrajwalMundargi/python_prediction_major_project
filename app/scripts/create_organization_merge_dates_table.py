# app/scripts/create_organization_merge_dates_table.py
"""
Script to create the organization_merge_dates table in the database.
This table stores merge dates along with organization information from github_metrics.
"""
from app.common.database import engine, Base
from app.models.organization_merge_dates import OrganizationMergeDate

def create_organization_merge_dates_table():
    """Create the organization_merge_dates table if it doesn't exist."""
    print("Creating organization_merge_dates table...")
    try:
        Base.metadata.create_all(bind=engine, tables=[OrganizationMergeDate.__table__])
        print("Organization merge dates table created successfully!")
    except Exception as e:
        print(f"ERROR: Error creating table: {e}")
        raise

if __name__ == "__main__":
    create_organization_merge_dates_table()

