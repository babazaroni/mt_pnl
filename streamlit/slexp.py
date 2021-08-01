import streamlit as st
import pandas as pd

col1, col2 = st.beta_columns([6,1])

col1.write('help')
col2.write('me')


st.sidebar.markdown('# sidebar')
st.write(""" #### My first app
 Hello *world!*"""
)
st.json({'foo':'bar'})

st.sidebar.selectbox(
    "how",('a','b')
)




selected_fruit = st.selectbox('Select a fruit',['a','b','c'])

options = st.multiselect('what colors',['green','yellow','red'])
st.write('you selected:',options)

st.write(pd.DataFrame({'first column': [1,2,3],'second column':[10,20,30]}))

st.table(["some text"])


container = st.beta_container()
container.write('this is name referenced container')
container.write('this is name referenced container')

items = [x for x in range(201)]

selection = st.sidebar.radio("text",items)

#https://blog.streamlit.io/introducing-new-layout-options-for-streamlit/


import streamlit as st
from string import ascii_uppercase, digits
from random import choices

img_base = "https://www.htmlcsscolor.com/preview/128x128/{0}.png"

colors = (''.join(choices(ascii_uppercase[:6] + digits, k=6)) for _ in range(100))

with st.beta_container():
    for col in st.beta_columns(3):
        col.image(img_base.format(next(colors)), use_column_width=True)


with st.beta_container():
    for col in st.beta_columns(4):
        col.image(img_base.format(next(colors)), use_column_width=True)


with st.beta_container():
    for col in st.beta_columns(10):
        col.image(img_base.format(next(colors)), use_column_width=True)

