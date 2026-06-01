import boto3
import os
from sqlalchemy import create_engine
import json

def connect_to_s3():
    access_key = os.getenv("AK")
    secret_key = os.getenv("SAK")
    region = os.getenv("REGION")
    bucket = os.getenv("BUCKET")

    s3 = boto3.client(
        's3',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )

    return s3, bucket

def create_db_engine():
    # create db engine
    db_url = os.getenv("DB_URL")
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    engine = create_engine(db_url)

    return engine

def load_json_file(s3,bucket,key):
    file = s3.get_object(Bucket=bucket, Key=key)
    content = file["Body"].read().decode("utf-8")
    data = json.loads(content)

    return data