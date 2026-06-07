import streamlit as st
import pandas as pd
import numpy as np
import json
from streamlit_lottie import st_lottie
import os

st.set_page_config(page_title = "SUPERSTORE", page_icon=":chart", layout = "centered")
st.title("SuperStore Group")

st.subheader("Intro")

st.subheader("Intro")
my_path1 = os.path.join("data","office.jpg")
st.image(my_path1, use_column_width="strecht")

st.markdown("""**SuperStore** is the leading group in the office technology, supplies and equipment sector in the *United States*. The group was founded over 30 years ago in Detroit (USA). It was the first 
        company to develop a B2B online purchasing platform for workplace materials 
        in 1999. Its catalogue includes technology products, supplies and office equipment. 
        Today, it has over 60,000 corporate customers in the USA.""")

st.write("Superstore")

with st.expander("Sustainability"):
    st.markdown("""SuperStore ensures that all steps taken to satisfy its customers are carried out in the 
most sustainable manner possible.""")
    st.markdown("""
        * More than half of the products are organic. \n
        * The group has reduced its CO2 emissions by a third (since 2010). \n
        * It has also minimised packaging and optimised its transport routes.""")
    
uploaded_file = st.file_uploader("Upload CSV", type = ["csv"])

if uploaded_file is not None:
    dataset = pd.read_csv(uploaded_file, parse_dates = ["Order Date"])
    dataset["Order Date Year"] = dataset["Order Date"].dt.strftime('%Y')
    
    if st.button("See data"):
        st.markdown("<h3 style='text-align: center; color:red;'>DataFrame (2013 - 2016)</h3>", unsafe_allow_html=True)
        st.dataframe(dataset)
        pivot_table = pd.pivot_table(dataset, values = "Sales", index = "Order Date Year",  columns = "Region", aggfunc = "sum").copy()
        st.markdown("<p style='text-align: center;'>Total sales per state (2013 - 2016)</p>", unsafe_allow_html=True)
        st.line_chart(pivot_table)
        st.balloons()
        st.snow()
        my_path = os.path.join("data", "animation.json")
        with open(my_path) as source:
            animation = json.load(source)
        st_lottie(animation, height=100, width=100)
