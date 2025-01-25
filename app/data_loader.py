import os

from io import StringIO

import boto3
import pandas as pd
import streamlit as st

from dotenv import load_dotenv


S3_CACHE_TTL = 300  # seconds
load_dotenv()


def load_data_local(file_path):
    df = pd.read_csv(file_path)
    df["Date"] = pd.to_datetime(df["Date"])  # Convert Date column to datetime
    return df


@st.cache_data(ttl=S3_CACHE_TTL)
def load_data_from_s3(bucket_name: str, file_name: str) -> pd.DataFrame:
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_DEFAULT_REGION"),
    )

    try:
        response = s3.get_object(Bucket=bucket_name, Key=file_name)
        csv_data = response["Body"].read().decode("utf-8")
        df = pd.read_csv(StringIO(csv_data))
        df["Date"] = pd.to_datetime(df["Date"])
        return df
    except Exception as exc:
        # Handle errors (e.g., file not found, permission issues)
        print(f"Error loading data from S3: {exc}")
        return pd.DataFrame()  # Return an empty DataFrame if there's an error
