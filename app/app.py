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

USE_DATE_FILTER = os.getenv("USE_DATE_FILTER", "False").lower() == "true"

RED_CELL_STYLE = (
    '<div style="background-color:#f0bbbe; padding:12px; border-radius:5px; border: 1px solid black;">'
)
GREEN_CELL_STYLE = (
    '<div style="background-color:#c5edc8; padding:12px; border-radius:5px; border: 1px solid black;">'
)
YELLOW_CELL_STYLE = (
    '<div style="background-color:#ede7c5; padding:12px; border-radius:5px; border: 1px solid black;">'
)

st.set_page_config(layout="wide")


st.write(f"### {CHART_HEADER}")

df, last_modified = load_data_from_s3(BUCKET_NAME, S3_FILE_NAME)

# Toggle visibility for each line
selected_items = st.multiselect(
    "Select Data to Display",  # Dropdown label
    options=[c.TRADER_PNL, c.CLIENT_PNL, c.AVAILABLE_BALANCE],  # Options for selection
    default=[c.TRADER_PNL, c.CLIENT_PNL, c.AVAILABLE_BALANCE],  # Default selected items
)

show_pnl = c.TRADER_PNL in selected_items
show_clean_pnl = c.CLIENT_PNL in selected_items
show_balance_change = c.AVAILABLE_BALANCE in selected_items


try:
    if USE_DATE_FILTER:
        start_date = st.date_input("Start Date", df[c.DATE].min())
        end_date = st.date_input("End Date", df[c.DATE].max())
        filtered_df = df[
            (df[c.DATE] >= pd.to_datetime(start_date)) & (df[c.DATE] <= pd.to_datetime(end_date))
        ]
    else:
        filtered_df = df
except DataLoadError as exc:
    st.error("Error loading data from S3")

except KeyError as exc:
    st.error(f"Failed to fetch the data. \n\n{exc!r}")
except Exception as exc:
    st.error(f"Failed to process the data. \n\n{exc!r}")
else:
    pnl_fig = plot_pnl(filtered_df, show_pnl, show_clean_pnl, show_balance_change)
    st.plotly_chart(pnl_fig)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"{RED_CELL_STYLE}Trader PnL: <b>{str(round(df[c.TRADER_PNL].iloc[-1] * 100, 2))}%</b> </div>",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"{GREEN_CELL_STYLE}Client PnL: <b>{str(round(df[c.CLIENT_PNL].iloc[-1] * 100, 2))}%</b> </div>",
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"{YELLOW_CELL_STYLE}Av. Balance: <b>{str(round(df[c.AVAILABLE_BALANCE].iloc[-1] * 100, 2))}%</b> </div>",
            unsafe_allow_html=True,
        )
    st.write("")

    if len(str(last_modified)) >= 19:  # ISO format date time
        st.info(f"Last data retrieval: {str(last_modified)[:19]} (UTC)")

    df = df.sort_values(by=[c.DATE], ascending=False)

    st.write("### Raw Data")
    st.dataframe(df, use_container_width=True, hide_index=True)
