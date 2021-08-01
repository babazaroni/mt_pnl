import json
import pandas as pd
import streamlit as st
import pandas as pd
from datetime import time
import requests
from random import random
import pprint
import timeit
from st_aggrid import GridOptionsBuilder, AgGrid, DataReturnMode, GridUpdateMode
import dateutil.parser

from slmt_utils import get_messages_as_df,format_date_series

#https://fullstackstation.com/streamlit-components-demo
#https://pypi.org/project/streamlit-aggrid/
#https://blog.ag-grid.com/wrapping-column-header-text/
#https://awesome-streamlit.org
#https://plotly.com/python/table/


st.set_page_config(layout='wide')

return_mode = st.sidebar.selectbox("Return Mode", list(DataReturnMode.__members__), index=1)
return_mode_value = DataReturnMode.__members__[return_mode]

update_mode = st.sidebar.selectbox("Update Mode", list(GridUpdateMode.__members__), index=6)
update_mode_value = GridUpdateMode.__members__[update_mode]

selection_mode = st.sidebar.radio("Selection Mode", ['single','multiple'])

groupSelectsChildren = st.sidebar.checkbox("Group checkbox select children", value=True)
groupSelectsFiltered = st.sidebar.checkbox("Group checkbox includes filtered", value=True)

df = get_messages_as_df().copy()
df.insert(0,"Timestamp",format_date_series(df['date']))

df['Col A'] = 0
df['Col B'] = 0
df['Col C'] = 0
df['Col D'] = 0
df['Col E'] = 0
df['Col F'] = 0
df['Col G'] = 0

gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum', editable=False,flex = 1,resizable=True,sortable=True,wrapText=False,autoHeight=True)
gb.configure_selection(selection_mode, use_checkbox=True, groupSelectsChildren=groupSelectsChildren, groupSelectsFiltered=groupSelectsFiltered)

gb.configure_column("date",hide = True)
gb.configure_column("Timestamp",type = 'rightAligned')
gb.configure_column("text",wrapText=True)

gb.configure_grid_options(domLayout='normal')
gridOptions = gb.build()



grid_response = AgGrid(
    df, 
    gridOptions = gridOptions,
    width='100%',
    data_return_mode=return_mode_value, 
    update_mode=update_mode_value,
    wrapText = True
    
    )

selected_list = grid_response['selected_rows']
selected_df = pd.DataFrame(selected_list)

print(selected_df)

#defaultColDef

print(str(gb))

print(random())
print('---------------------------------------')