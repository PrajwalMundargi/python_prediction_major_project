# app/models/historical_metrics.py
from sqlalchemy import Column, Integer, String, Float, DateTime
from app.common.database import Base

class HistoricalMetrics(Base):
    __tablename__ = "historical_metrics"

    id = Column(Integer, primary_key=True, index=True)
    organization_slug = Column(String, nullable=False, index=True)
    organization_name = Column(String, nullable=False)
    merge_frequency = Column(Float, nullable=False)
    total_prs = Column(Integer, default=0)
    merged_prs = Column(Integer, default=0)
    recorded_at = Column(DateTime, nullable=False, index=True)

