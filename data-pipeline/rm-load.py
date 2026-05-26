import os
from pprint import pprint
import pandas as pd
from sqlalchemy import create_engine, text
# from sqlalchemy.dialects.postgresql import ARRAY, TEXT
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
            latest_ep = conn.execute(text("select max(ep_id) from rm_episodes")).scalar()
            return 0 if latest_ep is None else latest_ep

    except Exception as e:
        print(f"Error: {e}")

def save_ep(latest_ep):
    try:
        df = pd.read_csv("cleaned_rm_episodes.csv")

        # 1. episodes: get only latest episode(s) and save to episodes table
        new_eps_df = df[df["ep_id"] > latest_ep]
        # filtered_df["teams"] = filtered_df["teams"].apply(lambda x: x.split(", ") if x != "No teams" else [])
        filtered_df = new_eps_df[["ep_id","aired_date","title","teams","mission","results"]]
        filtered_df.to_sql('rm_episodes', con=engine, if_exists='append', index=False)
        # filtered_df.to_sql('rm_episodes', con=engine, if_exists='append', index=False, dtype={"teams": ARRAY(TEXT)})
        print("episodes saved")
        return new_eps_df[["ep_id", "guests"]]

    except Exception as e:
        print(f"Error: {e}")

def save_guests(df):
    try:

        # 2. guests: explode list of guests into individual rows and get only unique names
        df["guests"] = df["guests"].str.split(', ')
        guests_df = df.explode('guests')
        guests_df = guests_df[~guests_df["guests"].str.startswith("(", na=False)]
        guests_df = guests_df[guests_df["guests"] != "No guest"]
        guests_df = guests_df.rename(columns={"guests":"guest_name"}) # col in table is guest_name

        # used for the rm_ep_guests junction table
        ep_guests_df = guests_df[["ep_id","guest_name"]]

        guests_df = guests_df[["guest_name"]].drop_duplicates()

        # get list of existing guests to check if it already exists
        existing_guests_df = pd.read_sql("select guest_name from rm_guests", engine)
        if not existing_guests_df.empty:
            existing_guests = existing_guests_df["guest_name"].tolist()
            new_guests_df = guests_df[~guests_df["guest_name"].isin(existing_guests)]
            # pprint(new_guests_df)
            if not new_guests_df.empty:
                new_guests_df.to_sql('rm_guests', con=engine, if_exists='append', index=False)
                print("new guests added")
            else:
                print("guest list is up to date")
        else:
#             pprint(guests_df)
            guests_df.to_sql('rm_guests', con=engine, if_exists='append', index=False)
            print("initial guest list added")

        return ep_guests_df

    except Exception as e:
        print(f"Error: {e}")

def save_ep_guest(df):
    try:

        # 3. episode-guest junction table
        # get unique guest ids from rm_guests table
        guest_df = pd.read_sql("select * from rm_guests", engine)

        # create dict for { 'guest_name' : guest_id }
        guest_name_id = dict(zip(guest_df["guest_name"], guest_df["guest_id"]))

        # map guest_id to ep_guests_df so it would be:
        # ep_id | guest_name | guest_id
        df["guest_id"] = df["guest_name"].map(guest_name_id)

        # only get ep_id and guest_id to save to junction table
        ep_guest_id_df = df[["ep_id","guest_id"]]

        # pprint(ep_guest_id_df)
        ep_guest_id_df.to_sql('rm_ep_guests', con=engine, if_exists='append', index=False)

        print("episodes and guests data added to db")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    latest_ep = check_eps()
    print(f"The latest ep is: {latest_ep}")
    episodes_df = save_ep(latest_ep)
    ep_guest_df = save_guests(episodes_df)
    save_ep_guest(ep_guest_df)