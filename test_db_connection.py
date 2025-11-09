# test_db_connection.py
from app.common.database import get_db_session
from app.models.github_metrics import GitHubMetrics
from sqlalchemy import text

session = get_db_session()

try:
    result = session.execute(text('SELECT COUNT(*) FROM gsoc_organizations;'))
    print("✅ Connected successfully.")
    print("Organizations in DB:", result.scalar())
except Exception as e:
    print("❌ Database error:", e)
finally:
    session.close()
