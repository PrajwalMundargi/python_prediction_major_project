# app/models/organization_merge_dates.py
"""
Model for storing merge dates along with organization information from github_metrics.
This table combines merge date data with organization metrics for easier querying.
"""
from sqlalchemy import Column, Integer, String, DateTime, Date
from app.common.database import Base


class OrganizationMergeDate(Base):
    __tablename__ = "organization_merge_dates"

    id = Column(Integer, primary_key=True, index=True)
    
    # Organization identification
    organization_slug = Column(String, nullable=False, index=True)
    organization_name = Column(String, nullable=False, index=True)
    
    # Merge date information
    merge_date = Column(Date, nullable=False, index=True)  # Date when merge happened
    merged_at = Column(DateTime, nullable=False)  # Full timestamp from GitHub
    merges_per_day = Column(Integer, nullable=False, default=0)  # Number of merges on this day
    
    # Organization information from github_metrics
    fetched_at = Column(DateTime, nullable=True)  # When github_metrics was fetched
    
    # Metadata
    created_at = Column(DateTime, nullable=False)  # When we recorded this merge date

