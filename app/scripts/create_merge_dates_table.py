# app/scripts/create_merge_dates_table.py
"""
Script to create the merge_dates table in the database.
"""
from app.common.database import engine, Base
from app.models.merge_dates import MergeDate

def create_merge_dates_table():
    """Create the merge_dates table if it doesn't exist."""
    print("Creating merge_dates table...")
    try:
        Base.metadata.create_all(bind=engine, tables=[MergeDate.__table__])
        print("Merge dates table created successfully!")
    except Exception as e:
        print(f"ERROR: Error creating table: {e}")
        raise

if __name__ == "__main__":
    create_merge_dates_table()

