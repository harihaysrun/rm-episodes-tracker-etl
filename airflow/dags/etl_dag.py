from datetime import timedelta, datetime
from airflow.models import DAG
from airflow.operators.python import PythonOperator

from dag.rm_scraper import run_scrape
from dag.rm_transform import run_transform
from dag.rm_load import run_load

def extract():
    run_scrape()

def transform():
    run_transform()

def load():
    run_load()

default_args = {
    'owner': 'me',
    'start_date': datetime(2026,6,2),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id="running_man",
    default_args=default_args,
    description="ETL pipeline for running man episode tracker",
    start_date=datetime(2026,6,2),
    # schedule_interval=timedelta(minutes=5),
    # schedule=timedelta(minutes=3),
    schedule=None,
    catchup=False,
    tags=['rm','dag','personal'],
) as dag:

    extract = PythonOperator(
        task_id="extract",
        python_callable=extract
    )

    transform = PythonOperator(
        task_id="transform",
        python_callable=transform
    )

    load = PythonOperator(
        task_id="load",
        python_callable=load
    )

    extract >> transform >> load