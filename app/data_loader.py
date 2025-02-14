import os
import sys

from io import StringIO

import boto3
import constants as c
import pandas as pd
import streamlit as st

from dotenv import load_dotenv


S3_CACHE_TTL = 300  # seconds
load_dotenv()


def load_data_local(file_path):
    df = pd.read_csv(file_path)
    df[c.DATE] = pd.to_datetime(df[c.DATE])  # Convert Date column to datetime
    return df


class DataLoadError(Exception):
    pass


@st.cache_data(ttl=S3_CACHE_TTL)
def load_data_from_s3(bucket_name: str, file_name: str) -> tuple[pd.DataFrame, str]:
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_DEFAULT_REGION"),
    )

    try:
        response = s3.get_object(Bucket=bucket_name, Key=file_name)
        csv_data = response["Body"].read().decode("utf-8")
        last_modified = response["LastModified"]
        df = pd.read_csv(
            StringIO(csv_data),
            dtype={c.TRADER_PNL: float, c.CLIENT_PNL: float, c.AVAILABLE_BALANCE: float},
        )

        _prepare_dataframe(df)
        return df, last_modified
    except Exception:
        sys.tracebacklimit = 0
        raise DataLoadError("Error loading data from S3")


def _prepare_dataframe(df: pd.DataFrame) -> None:
    df[c.DATE] = pd.to_datetime(df[c.DATE], format="ISO8601")
