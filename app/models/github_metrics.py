from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from app.common.database import Base

class GitHubMetrics(Base):
    __tablename__ = "github_metrics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    github_followers = Column(Integer)
    github_repos = Column(Integer)
    github_bio = Column(Text)
    fetched_at = Column(DateTime)

    # New fields
    pull_requests = Column(Integer, default=0)
    merged_prs = Column(Integer, default=0)
    merge_frequency = Column(Float, default=0.0)  # e.g., merges per week
