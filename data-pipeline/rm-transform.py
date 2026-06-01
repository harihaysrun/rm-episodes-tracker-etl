from pprint import pprint
import pandas as pd
import json
from connect import connect_to_s3, load_json_file

def run_transform():
    data = load_json_file(s3,bucket, "rm_episodes.json")

    df = pd.DataFrame(data)
    print(df)

    df.rename(columns={
        'Ep.': 'ep_id',
        'Airdate|(Filming date)': 'aired_date',
        'Title': 'title',
        'Guest(s)': 'guests',
        'Teams': 'teams',
        'Mission': 'mission',
        'Results': 'results'
    }, inplace=True)

    df = df[~df["ep_id"].str.contains("Special")]
    df["ep_id"] = df["ep_id"].str[:3].astype(int)

    df["aired_date"] = df["aired_date"].str.split("|").str[0]
    # df["aired_date"] = pd.to_datetime(df["aired_date"])

    df["guests"] = df["guests"].str.replace("|", ", ")

    cols_to_clean = ["title","teams","mission","results"]
    for col in cols_to_clean:
        df[col] = df[col].str.replace("|", " ")

    df.to_json("cleaned_rm_episodes.json", orient="records", indent=4, force_ascii=False)

    s3.upload_file("cleaned_rm_episodes.json", bucket, "cleaned_rm_episodes.json")

if __name__ == "__main__":
    s3, bucket = connect_to_s3()
    run_transform()