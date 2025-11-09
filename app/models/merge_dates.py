# app/models/merge_dates.py
from sqlalchemy import Column, Integer, String, DateTime, Date
from app.common.database import Base

class MergeDate(Base):
    __tablename__ = "merge_dates"

    id = Column(Integer, primary_key=True, index=True)
    organization_slug = Column(String, nullable=False, index=True)
    organization_name = Column(String, nullable=False)
    merge_date = Column(Date, nullable=False, index=True)  # Date when merge happened
    merged_at = Column(DateTime, nullable=False)  # Full timestamp from GitHub
    repository_name = Column(String, nullable=True)  # Which repo the merge was in
    pull_request_number = Column(Integer, nullable=True)  # PR number
    created_at = Column(DateTime, nullable=False)  # When we recorded this

