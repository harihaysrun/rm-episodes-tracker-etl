from flask import Flask, render_template, request, jsonify
import os
from pprint import pprint
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

app = Flask(__name__)

episodes_df = pd.read_sql("select * from rm_episodes", engine)
episodes = episodes_df.to_dict(orient="records")
unique_guests_df = pd.read_sql("select * from rm_guests", engine)
unique_guests = unique_guests_df.sort_values("guest_name").to_dict(orient="records")
guests_df = pd.read_sql("select * from guests_per_ep", engine)
guests_list = guests_df.groupby("ep_id")["guest_name"].apply(list).to_dict()

def filter_episodes(episodes, guests):
    guest_id = request.args.get("guest", "").strip()
    # no_guest = request.args.get("no_guest") == "1"
    sort = request.args.get("sort", "recent")
    year = request.args.get("year", "")

    filtered_episodes = episodes
    if guest_id != "":
        if guest_id != "0":
            selected_episodes = guests_df.loc[guests_df["guest_id"] == int(guest_id), "ep_id"].tolist()
            # pprint(guest_id)
            filtered_episodes = [
                episode for episode in filtered_episodes if episode["ep_id"] in selected_episodes
            ]
        else: # no guest
            filtered_episodes = [
                episode for episode in filtered_episodes if episode["ep_id"] not in guests_df["ep_id"].to_list()
            ]
    if year and year != "All":
        filtered_episodes = [
            episode for episode in filtered_episodes if episode["aired_date"].year == int(year)
        ]
    filtered_episodes = sorted(
        filtered_episodes,
        key=lambda episode: episode["aired_date"],
        reverse=sort != "oldest",
    )

    # guests = sorted({episode["ep_id"] for episode in episodes})

    filters = {"guest": guest_id, "sort": sort, "year": year}

    return filtered_episodes, filters

def get_watchlist():
    watchlist_df = pd.read_sql("select * from rm_watchlist", engine)
    return watchlist_df

@app.route("/")
def index():
    filtered_episodes, filters = filter_episodes(episodes, guests_df)

    watchlist_df = get_watchlist()
    watchlist = watchlist_df["ep_id"].to_list()

    pprint(watchlist)

    # pprint(filters)
    # pprint(filtered_episodes)
    return render_template(
        "index.html",
        title="Home",
        episodes=filtered_episodes,
        guests=unique_guests,
        watchlist=watchlist,
        guests_list=guests_list,
        filters=filters
    )

@app.route("/watchlist")
def watchlist():

    watchlist_df = get_watchlist()
    watchlist = watchlist_df.sort_values("ep_id").to_dict(orient="records")

    episode_lookup = {ep['ep_id']: ep for ep in episodes}
    # pprint(episode_lookup)

    return render_template(
        "watchlist.html",
        title="Watchlist",
        episode_lookup=episode_lookup,
        watchlist=watchlist,
        guests_list=guests_list,
    )

@app.route("/add", methods=["POST"])
def watchlist_add():
    if request.method == "POST":
        data = request.get_json()
        ep_id = data.get("ep_id")

        with engine.connect() as conn:
            conn.execute(text("insert into rm_watchlist (ep_id) values (:ep_id)"), {"ep_id": int(ep_id)})
            conn.commit()

        return jsonify({
            "status" : "added to watchlist successfully",
            "redirect_url":"/watchlist"
        })

@app.route("/remove", methods=["POST"])
def watchlist_remove():
    if request.method == "POST":
        data = request.get_json()
        ep_id = data.get("ep_id")

        with engine.connect() as conn:
            conn.execute(text("delete from rm_watchlist where ep_id = (:ep_id)"), {"ep_id": int(ep_id)})
            conn.commit()

        return jsonify({
            "status" : "deleted from watchlist successfully",
            "redirect_url":"/watchlist"
        })

@app.route("/watched", methods=["POST"])
def watchlist_watched():
    if request.method == "POST":
        data = request.get_json()
        ep_id = data.get("ep_id")

        with engine.connect() as conn:
            conn.execute(text("update rm_watchlist set watched = 'yes' where ep_id = (:ep_id)"), {"ep_id": int(ep_id)})
            conn.commit()

        return jsonify({
            "status" : "episode marked as watched",
            "redirect_url":"/watchlist"
        })

if __name__ == "__main__":
    app.run(debug=True)
