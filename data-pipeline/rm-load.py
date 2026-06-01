import os
from pprint import pprint
import pandas as pd
from sqlalchemy import text
from connect import create_db_engine, connect_to_s3, load_json_file

engine = create_db_engine()
s3, bucket = connect_to_s3()

def check_eps():
    try:
        with engine.connect() as conn:
            latest_ep = conn.execute(text("select max(ep_id) from rm_episodes")).scalar()
            return 0 if latest_ep is None else latest_ep

    except Exception as e:
        print(f"Error: {e}")

def save_ep(latest_ep):
    try:
        data = load_json_file(s3, bucket, "cleaned_rm_episodes.json")
        df = pd.DataFrame(data)
        # print(df)

        # 1. episodes: get only latest episode(s) and save to episodes table
        new_eps_df = df[df["ep_id"] > latest_ep]
        filtered_df = new_eps_df[["ep_id","aired_date","title","teams","mission","results"]]
        # pprint(filtered_df)
        filtered_df.to_sql('rm_episodes', con=engine, if_exists='append', index=False)
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
        pprint(guests_df)

        if not guests_df.empty:
            query = text('''
            INSERT INTO rm_guests (guest_name)
            VALUES (:guest_name)
            ON CONFLICT (guest_name) DO NOTHING
            ''')

            with engine.begin() as conn:
                conn.execute(query, guests_df.to_dict("records"))
                conn.execute(text("REFRESH MATERIALIZED VIEW guests_per_ep"))
                print("guests added")

        else:
            print("no new guests")

        return ep_guests_df

    except Exception as e:
        print(f"Error: {e}")

def save_ep_guest(df):
    try:

        if not df.empty:
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
        else:
            print("no new guests to add")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    latest_ep = check_eps()
    print(f"The latest ep is: {latest_ep}")
    episodes_df = save_ep(latest_ep)
    ep_guest_df = save_guests(episodes_df)
    save_ep_guest(ep_guest_df)