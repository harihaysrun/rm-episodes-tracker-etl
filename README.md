# Running Man Episode Tracker

A fully automated ETL pipeline that scrapes, processes, and loads *Running Man* episode data into a database for use in a front-end interface with search, filtering, and watchlist functionality.

### Tech Stack
- **Data & ETL:** Python, Pandas, PostgreSQL, SQLAlchemy
- **Orchestration & automation:** GitHub Actions, Apache Airflow
- **Cloud storage:** AWS S3
- **Containerisation & infrastructure:** Docker
- **Web application:** Flask, Jinja2

## How the pipeline works

### 1. Extraction (E): Web scraping
`rm-scraper.py` initiates by accessing the [Running Man episode list on Wikipedia](https://en.wikipedia.org/wiki/List_of_Running_Man_episodes_(2026)) using `BeautifulSoup4`. Due to the complex structure of the HTML table (with multiple rowspans), data is stored in a grid list to preserve the exact positioning of the cell values before being saved in a JSON file stored in S3.
* Removal of HTML tags is performed during this step.

### 2. Transformation (T): Data refinement
The JSON file is processed by `rm-transform.py`, which uses `pandas` for data transformation and preparation. This stage includes:
* **Normalisation:** Standardising column headers and data formats.
* **Data cleaning:** Fixing data types and converting structured fields (e.g., guest lists) into a consistent format.
* **Validation:** Ensuring the output is clean and ready for the loading phase.

### 3. Loading (L): Database persistence
`rm-load.py` loads the cleaned JSON data into the PostgreSQL database using `pandas` and `SQLAlchemy`:

* **Data ingestion:** Transfers transformed DataFrames into PostgreSQL efficiently.
* **Production practices:** Uses context managers for safe connection handling and parameterised operations for secure data loading.

<details>
<summary><b>Click here to view the database schema (ERD)</b></summary>

![Database Schema](database/erd-model.png)
</details>



## Automation with GitHub Actions
The pipeline is orchestrated using **GitHub Actions** for automated scheduled execution, providing a lightweight alternative to Apache Airflow.
* A cron-based workflow triggers the Python scripts in sequence on a weekly schedule. This creates a "set-and-forget" data environment where the database is continuously kept in sync with the latest episodes.


## Full-stack dashboard & watchlist

<details>
<summary><b>Click here to view the UI</b></summary>

![Home page](web-app/ui/1.png)
![Watchlist](web-app/ui/2.png)
</details>

Beyond the engineering pipeline, this project includes an interactive web dashboard built on `Flask` and `Jinja2`. This serves as the visualisation layer, allowing users to:
* **Explore episodes:** Search and filter through the complete episode database.
* **Personal watchlist:** Maintain a custom state for episodes, demonstrating basic CRUD (Create, Read, Update, Delete) capabilities within the web app.


## Project Structure

```text
rm-episodes-tracker-etl/
├── .github/workflows/    # CI/CD pipelines
├── database/             # SQL schema
├── data-pipeline/        # Core ETL logic (scraper, transform, load) & requirements.txt for cron job
└── web-app/              # Flask dashboard (templates, static assets, app.py)