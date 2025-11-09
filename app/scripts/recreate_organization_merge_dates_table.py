# app/scripts/recreate_organization_merge_dates_table.py
"""
Script to drop and recreate the organization_merge_dates table with updated schema.
WARNING: This will delete all existing data in the table!
"""
from app.common.database import engine, Base
from app.models.organization_merge_dates import OrganizationMergeDate
from sqlalchemy import text

def recreate_organization_merge_dates_table():
    """Drop and recreate the organization_merge_dates table."""
    print("Recreating organization_merge_dates table...")
    print("WARNING: This will delete all existing data!")
    
    try:
        # Drop the table if it exists
        with engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS organization_merge_dates"))
            conn.commit()
        print("Dropped existing table")
        
        # Create the new table with updated schema
        Base.metadata.create_all(bind=engine, tables=[OrganizationMergeDate.__table__])
        print("Organization merge dates table recreated successfully!")
        print("New schema includes:")
        print("   - id")
        print("   - organization_slug")
        print("   - organization_name")
        print("   - merge_date")
        print("   - merged_at")
        print("   - merges_per_day")
        print("   - fetched_at")
        print("   - created_at")
    except Exception as e:
        print(f"ERROR: Error recreating table: {e}")
        raise

if __name__ == "__main__":
    recreate_organization_merge_dates_table()

