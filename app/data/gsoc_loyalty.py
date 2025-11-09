import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URI = os.getenv("DATABASE_URI")

def fetch_org_data():
    print("Fetching org data from DB...")
    engine = create_engine(DATABASE_URI)
    query = "SELECT name, year FROM gsoc_organizations;"
    df = pd.read_sql_query(query, engine)
    print(f"Retrieved {len(df)} entries.")
    return df

def compute_loyalty(df):
    loyalty_df = df.groupby("name")["year"].nunique().reset_index()
    loyalty_df.columns = ["organization_name", "years_active"]

    streaks = []
    for org, subdf in df.groupby("name"):
        years = sorted(subdf["year"].unique())
        max_streak, current = 1, 1
        for i in range(1, len(years)):
            if years[i] == years[i - 1] + 1:
                current += 1
            else:
                current = 1
            max_streak = max(max_streak, current)
        streaks.append({"organization_name": org, "loyalty_streak": max_streak})
    
    streaks_df = pd.DataFrame(streaks)
    result = pd.merge(loyalty_df, streaks_df, on="organization_name", how="left")
    result.to_csv("loyalty_scores.csv", index=False)
    print("Saved loyalty scores to app/data/loyalty_scores.csv")
    return result

if __name__ == "__main__":
    df = fetch_org_data()
    compute_loyalty(df)
