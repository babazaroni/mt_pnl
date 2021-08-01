import sys
sys.path.append("/home/cc/options/process/python/MasterTrader")


import json
import pandas as pd
import streamlit as st
import pandas as pd
from datetime import time
import requests
from random import random
import pprint
import timeit
from streamlit import caching

import dateutil.parser

from slmt_utils import get_messages_as_df,format_date_series
from slmt_parse import get_tokens,get_token_strings,get_actions
from mt_data import *
from slmt_backtest import *

#https://fullstackstation.com/streamlit-components-demo
#https://pypi.org/project/streamlit-aggrid/
#https://blog.ag-grid.com/wrapping-column-header-text/
#https://awesome-streamlit.org
#https://plotly.com/python/table/


st.set_page_config(layout='wide')

#caching.clear_cache()

#hack to align dataframe content to left
#does not seem to work
st.markdown(
    """<style>
    .dataframe {text-align: left !important}
    <Style>
    """, unsafe_allow_html = True
)

DEFAULT_NUMBER_OF_ROWS = 5
DEFAULT_NUMBER_OF_COLUMNS = 5


def has_numbers(input):
    return any(char.isdigit() for char in input)

def select_symbols_to_display(df):

    syms = []
    for t in df['text']:
    
        for w in t.split():
            if w.isalpha() and w.isupper() and len(w)<=5:
                syms.append(w)

    syms = list(set(syms)) #make unique list

    syms.sort()

    syms.insert(0,'All')

    #syms = ['AAL']

    symbol = st.sidebar.selectbox(
        "Select symbol to display",
        options = syms,
        key = 'select_symbols'
    )
    return symbol

def select_index_range(results):
    start = st.sidebar.slider("select start index",
        0,
        len(results),
        0
    )
    return start

def select_count_to_display(results):
    count = st.sidebar.slider("select count to display",
        0,
        len(results),
        len(results)
    )
    return count

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



#@st.cache
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
            props=[("font-size", "150%"), ("text-align", "left"), ("color", "red")],
        ),
        dict(selector="caption", props=[("caption-side", "bottom")]),
    ]
    return (
        results.style.set_table_styles(table_styles)
        .set_properties(**{"background-color": "blue", "color": "white"})
        .set_caption("This is a caption")
    )

def streamlit_table(results):
    table = st.table(results)
    return table
    number_of_rows, number_of_columns, style = select_number_of_rows_and_columns(
        results, key="st.table"
    )


    filter_table = filter_results(results, number_of_rows, number_of_columns, style)
    table = st.table(filter_table)

    return table

@st.cache
def sl_data_init_underlying():
    underlying_cache = download_data(underlying_urls)

    print('underlying_cache:',len(underlying_cache))

    if len(underlying_cache):
        prepare_underlying_cache(underlying_cache)

    return underlying_cache


@st.cache
def sl_data_init_options():

    options_cache = download_data(option_urls)
    
    print('options_cache:',len(options_cache))

    if len(options_cache):
        prepare_options_cache(options_cache)

    return options_cache


df = get_messages_as_df().copy()
df.insert(0,"Timestamp",format_date_series(df['date']))

symbol = select_symbols_to_display(df)
start = select_index_range(df)

if symbol is not 'All':
    print('looking for',symbol)
    df = df[df['text'].str.contains(symbol)]

df = df[start:]

count = select_count_to_display(df)

df = df[0:count]


tokens = get_tokens(df['date'],df['text'])
df['tokens'] = get_token_strings(tokens)

actions = get_actions(tokens,df['date'],df['text'])
df['actions'] = get_token_strings(actions)




options = ['Parse Only','Add Backtest']
display = st.sidebar.radio('backtest',options)
display_selection = options.index(display)


import time

hide_columns = ['date']

if display_selection == 1:


    underlying_data = sl_data_init_underlying()
    options_data = sl_data_init_options()

    data_global_set(options_data,underlying_data)

    df_backtest,backtest_hidden_columns = get_backtest_df(df['date'],actions)

    df = pd.concat([df,df_backtest],axis = 1)

    hide_columns.extend(backtest_hidden_columns)

    pprint.pprint(df)

    print("gide_col",hide_columns)
    print("sdfd",backtest_hidden_columns)


    print("sum of premiums",sum(df['premium_data']))


 

print("hide_columns",hide_columns)
streamlit_table(df.drop(hide_columns,axis=1))


print(random())
print('---------------------------------------')