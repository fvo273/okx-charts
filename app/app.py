import os

import constants as c
import pandas as pd
import streamlit as st

from data_loader import DataLoadError
from data_loader import load_data_from_s3
from dotenv import load_dotenv
from utils import Exchanges
from utils import PnlCellStyles
from visualizations import plot_pnl


load_dotenv()

BUCKET_NAME = os.getenv("AWS_BUCKET_NAME", "")
S3_FILE_NAME = os.getenv("AWS_S3_FILE_NAME", "")
CHART_HEADER = os.getenv("CHART_HEADER", "Statement")
USE_DATE_FILTER = os.getenv("USE_DATE_FILTER", "False").lower() == "true"

APP_VERSION = "0.1.25"

st.set_page_config(layout="wide")


def okx_dashboard():
    st.write(f"### {CHART_HEADER} - {Exchanges.OKX}")

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
                f"{PnlCellStyles.RED}Trader PnL: <b>{str(round(df[c.TRADER_PNL].iloc[-1] * 100, 2))}%</b> </div>",
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f"{PnlCellStyles.GREEN}Client PnL: <b>{str(round(df[c.CLIENT_PNL].iloc[-1] * 100, 2))}% *</b> </div>",
                unsafe_allow_html=True,
            )
        with col3:
            st.markdown(
                f"{PnlCellStyles.YELLOW}Av. Balance: <b>{str(round(df[c.AVAILABLE_BALANCE].iloc[-1] * 100, 2))}%</b> </div>",
                unsafe_allow_html=True,
            )

        st.write("")
        st.markdown(
            "<div> * Starting on February 18, the profit distribution will be 100% for the client and 0% for the trader.</div>",
            unsafe_allow_html=True,
        )
        st.write("")

        if len(str(last_modified)) >= 19:  # ISO format date time
            st.info(f"Last data retrieval: {str(last_modified)[:19]} (UTC)")

        df = df.sort_values(by=[c.DATE], ascending=False)

        st.write("### Raw Data")
        st.dataframe(df, use_container_width=True, hide_index=True)


def bingx_dashboard():
    st.write(f"### {CHART_HEADER} - {Exchanges.BINGX}")
    st.write("Coming soon!")


def bitget_dashboard():
    st.write(f"### {CHART_HEADER} - {Exchanges.BITGET}")
    st.write("Coming soon!")


# Sidebar menu for navigation
menu_options = [Exchanges.OKX, Exchanges.BINGX, Exchanges.BITGET]
selected_dashboard = st.sidebar.radio("Select an exchange", menu_options)

# Call the appropriate dashboard function based on selection
if selected_dashboard == Exchanges.OKX:
    okx_dashboard()
elif selected_dashboard == Exchanges.BINGX:
    bingx_dashboard()
elif selected_dashboard == Exchanges.BITGET:
    bitget_dashboard()

for _ in range(10):
    st.sidebar.write(" ")

st.sidebar.markdown(f'<div style="color:#d9d9d9">v. {APP_VERSION}</div>', unsafe_allow_html=True)
