# app/scripts/create_historical_table.py
"""
Script to create the historical_metrics table in the database.
Run this once to set up the table for tracking merge frequency over time.
"""
from app.common.database import engine, Base
from app.models.historical_metrics import HistoricalMetrics

def create_historical_table():
    """Create the historical_metrics table if it doesn't exist."""
    print("Creating historical_metrics table...")
    try:
        Base.metadata.create_all(bind=engine, tables=[HistoricalMetrics.__table__])
        print("Historical metrics table created successfully!")
    except Exception as e:
        print(f"ERROR: Error creating table: {e}")
        raise

if __name__ == "__main__":
    create_historical_table()

