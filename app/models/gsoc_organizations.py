# app/models/gsoc_organizations.py
from sqlalchemy import Column, Integer, String, Text, JSON, TIMESTAMP
from app.common.database import Base

class GSoCOrganization(Base):
    __tablename__ = "gsoc_organizations"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(Text, unique=True)
    name = Column(Text)
    logo_url = Column(Text)
    website_url = Column(Text)
    tagline = Column(Text)
    contact_links = Column(JSON)
    date_created = Column(TIMESTAMP)
    tech_tags = Column(JSON)
    topic_tags = Column(JSON)
    categories = Column(JSON)
    program_slug = Column(Text)
    logo_bg_color = Column(Text)
    description_html = Column(Text)
    ideas_list_url = Column(Text)
    github_url = Column(Text)
    github_followers = Column(Integer)
    github_repos = Column(Integer)
    github_bio = Column(Text)
    year = Column(Integer)
    fetched_at = Column(TIMESTAMP)
