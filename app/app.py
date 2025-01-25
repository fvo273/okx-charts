import os

import constants as c
import pandas as pd
import streamlit as st

from data_loader import DataLoadError
from data_loader import load_data_from_s3
from dotenv import load_dotenv
from visualizations import plot_pnl


load_dotenv()

BUCKET_NAME = os.getenv("AWS_BUCKET_NAME", "")
S3_FILE_NAME = os.getenv("AWS_S3_FILE_NAME", "")
CHART_HEADER = os.getenv("CHART_HEADER", "Statement")

st.write(f"### {CHART_HEADER}")

df = load_data_from_s3(BUCKET_NAME, S3_FILE_NAME)

# Toggle visibility for each line
show_pnl = st.checkbox(c.TRADER_PNL, value=True)
show_clean_pnl = st.checkbox(c.CLIENT_PNL, value=True)
show_balance_change = st.checkbox(c.AVAILABLE_BALANCE, value=True)

try:
    start_date = st.date_input("Start Date", df[c.DATE].min())
    end_date = st.date_input("End Date", df[c.DATE].max())
    filtered_df = df[
        (df[c.DATE] >= pd.to_datetime(start_date)) & (df[c.DATE] <= pd.to_datetime(end_date))
    ]
except DataLoadError as exc:
    st.error("Error loading data from S3")

except KeyError as exc:
    st.error(f"Failed to fetch the data. \n\n{exc!r}")
except Exception as exc:
    st.error(f"Failed to process the data. \n\n{exc!r}")
else:
    pnl_fig = plot_pnl(filtered_df, show_pnl, show_clean_pnl, show_balance_change)
    st.plotly_chart(pnl_fig)

    st.write("### Raw Data")
    st.dataframe(df, use_container_width=True, hide_index=True)
