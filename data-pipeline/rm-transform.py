from pprint import pprint
import pandas as pd

df = pd.read_excel("rm_episodes.xlsx")

df.rename(columns={
    'Ep.': 'ep_id',
    'Airdate|(Filming date)': 'aired_date',
    'Title': 'title',
    'Guest(s)': 'guests',
    'Teams': 'teams',
    'Mission': 'mission',
    'Results': 'results'
}, inplace=True)

df["ep_id"] = df["ep_id"].str[:3].astype(int)

df["aired_date"] = df["aired_date"].str.split("|").str[0]
df["aired_date"] = pd.to_datetime(df["aired_date"])

df["guests"] = df["guests"].str.replace("|", ", ")

cols_to_clean = ["title","teams","mission","results"]
for col in cols_to_clean:
    df[col] = df[col].str.replace("|", " ")

df.to_csv("cleaned_rm_episodes.csv", index=False)