import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pathlib import Path

# create db engine
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)
db_url = os.getenv("DB_URL")
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

engine = create_engine(db_url)

def check_eps():
    try:
        with engine.connect() as conn:
            latest_ep = conn.execute(text("select max(ep_no) from rm_episodes")).scalar()
            return latest_ep

    except Exception as e:
        print(f"Error: {e}")

def save_ep(latest_ep):
    try:
        df = pd.read_csv("cleaned_rm_episodes.csv")

        # get only latest episode(s) and save to db
        filtered_df = df[df["ep_no"] > latest_ep]
        filtered_df.to_sql('rm_episodes', con=engine, if_exists='append', index=False)

        print("Data loaded successfully!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    latest_ep = check_eps()
    print(f"The latest ep is: {latest_ep}")
    save_ep(latest_ep)