import json
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import time
import requests
from random import random
import pprint
import timeit

import dateutil.parser

from slmt_utils import get_messages_as_df,format_date_series

#https://fullstackstation.com/streamlit-components-demo
#https://pypi.org/project/streamlit-aggrid/
#https://blog.ag-grid.com/wrapping-column-header-text/
#https://awesome-streamlit.org
#https://plotly.com/python/table/


#st.set_page_config(layout='wide')

DEFAULT_NUMBER_OF_ROWS = 5
DEFAULT_NUMBER_OF_COLUMNS = 5


def select_number_of_rows_and_columns(results: pd.DataFrame, key: str):
    rows = st.selectbox(
        "Select number of table rows to display",
        options=[5, 10, 50, 100, 500, 1000, 5000, 10000, 50000, len(results)],
        key=key,
    )
    columns = st.slider(
        "Select number of table columns to display",
        0,
        len(results.columns) - 1,
        DEFAULT_NUMBER_OF_COLUMNS,
        key=key,
    )
    style = st.checkbox("Style dataframe?", False, key=key)
    return rows, columns, style



@st.cache
def _filter_results(results, number_of_rows, number_of_columns) -> pd.DataFrame:
    return results.iloc[0:number_of_rows, 0:number_of_columns]


def filter_results(results, number_of_rows, number_of_columns, style) -> pd.DataFrame:
    filter_table = _filter_results(results, number_of_rows, number_of_columns)
    if style:
        filter_table = set_styles(filter_table)
    return filter_table


def set_styles(results):
    table_styles = [
        dict(
            selector="table",
            props=[("font-size", "150%"), ("text-align", "center"), ("color", "red")],
        ),
        dict(selector="caption", props=[("caption-side", "bottom")]),
    ]
    return (
        results.style.set_table_styles(table_styles)
        .set_properties(**{"background-color": "blue", "color": "white"})
        .set_caption("This is a caption")
    )

def plotly_table(results):
    st.header("Plotly Table (go.Table)")
    number_of_rows, number_of_columns, style = select_number_of_rows_and_columns(
        results, key="go.Table"
    )
    filter_table = _filter_results(results, number_of_rows, number_of_columns)

    header_values = list(filter_table.columns)
    cell_values = []
    for index in range(0, len(filter_table.columns)):
        cell_values.append(filter_table.iloc[:, index : index + 1])

    if not style:
        fig = go.Figure(
            data=[
                go.Table(
                    header=dict(values=header_values), cells=dict(values=cell_values)
                )
            ]
        )
    else:
        fig = go.Figure(
            data=[
                go.Table(
                    header=dict(
                        values=header_values, fill_color="paleturquoise", align="left"
                    ),
                    cells=dict(values=cell_values, fill_color="lavender", align="left"),
                )
            ]
        )

    st.plotly_chart(fig)


df = get_messages_as_df().copy()
df.insert(0,"Timestamp",format_date_series(df['date']))

df['Col A'] = 0
df['Col B'] = 0
df['Col C'] = 0
df['Col D'] = 0
df['Col E'] = 0
df['Col F'] = 0
df['Col G'] = 0

plotly_table(df)






print(random())
print('---------------------------------------')