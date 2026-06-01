import pandas as pd
import requests
from bs4 import BeautifulSoup
# from pprint import pprint
from connect import connect_to_s3

def run_scrape():

    user_agent = {'User-agent': 'Mozilla/5.0'}
    BASE_URL = 'https://en.wikipedia.org/wiki/'
    page = requests.get(BASE_URL + 'List_of_Running_Man_episodes_(2025)', headers = user_agent)
    soup = BeautifulSoup(page.content, "html.parser")

    tables = soup.find_all('table',{'class':'wikitable'})
    table = tables[0]
    rows = table.find_all("tr")

    # pre-calculate the grid size to prevent shifting
    num_rows = len(rows)
    num_cols = 7

    # empty grid filled with None placeholders
    grid = [[None for _ in range(num_cols)] for _ in range(num_rows)]

    # map data into grid
    for row_id, row in enumerate(rows):
        cols = row.find_all(["td", "th"])

        col_id = 0
        for cell in cols:
            # Move to the next available empty slot in our grid row
            while col_id < num_cols and grid[row_id][col_id] is not None:
                col_id += 1

            if col_id >= num_cols:
                break

            # remove html syntax from text
            for br in cell.find_all("br"):
                br.replace_with("|")
            cell_text = cell.text.strip()

            # look for rowspan attribute
            if cell.has_attr('rowspan'):
                row_count = int(cell['rowspan'])
                # fill the current cell and all blocked cells below it with the same text
                for i in range(row_count):
                    if row_id + i < num_rows:
                        grid[row_id + i][col_id] = cell_text
            else:
                grid[row_id][col_id] = cell_text

            col_id += 1

    # export as json file
    headers = grid[0]
    ep_rows = grid[1:]

    df = pd.DataFrame(ep_rows, columns = headers)
    df.to_json("rm_episodes.json", orient="records", indent=4, force_ascii=False)
    # json_string = df.to_json(orient="records")

    s3.upload_file("rm_episodes.json", bucket, "rm_episodes.json")

if __name__ == "__main__":
    s3, bucket = connect_to_s3()
    run_scrape()