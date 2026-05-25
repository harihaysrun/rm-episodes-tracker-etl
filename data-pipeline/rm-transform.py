from pprint import pprint
import pandas as pd

df = pd.read_excel("rm_episodes.xlsx")

df.rename(columns={
    'Ep.': 'ep_no',
    'Airdate|(Filming date)': 'aired_date',
    'Title': 'title',
    'Guest(s)': 'guests',
    'Teams': 'teams',
    'Mission': 'mission',
    'Results': 'results'
}, inplace=True)

df["ep_no"] = df["ep_no"].str[:3].astype(int)

df["aired_date"] = df["aired_date"].str.split("|").str[0]
df["aired_date"] = pd.to_datetime(df["aired_date"])

df[["title","guests","teams","mission","results"]] = df[["title","guests","teams","mission","results"]].replace("|", " ")

print(df)
print(df.dtypes)