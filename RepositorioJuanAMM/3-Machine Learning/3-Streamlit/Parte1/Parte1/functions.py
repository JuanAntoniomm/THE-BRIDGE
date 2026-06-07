import streamlit as st
import json
import pandas as pd
from streamlit_lottie import st_lottie
from PIL import Image
import numpy as np
import plotly.express as px
import pydeck as pdk
import os


def config_page():
    st.set_page_config(page_title = "SUPERSTORE", page_icon=":chart:", layout="centered")

def home():
    st.title("Grupo SuperStore")

    st.subheader("Intro")
    
    my_path1 = os.path.join("data","office.jpg")
    img = Image.open(my_path1)
    st.image(img, use_column_width=True)

    st.markdown("""**SuperStore** is the leading group in the office technology, supplies and equipment sector in the *United States*. The group was founded over 30 years ago in Detroit (USA). It was the first 
        company to develop a B2B online purchasing platform for workplace materials 
        in 1999. Its catalogue includes technology products, supplies and office equipment. 
        Today, it has over 60,000 corporate customers in the USA.""")

    with st.expander("Sustainability"):
        st.markdown("""SuperStore ensures that all steps taken to satisfy its customers are carried out in the 
most sustainable manner possible.""")
        st.markdown("""
        * More than half of the products are organic. \n
        * The group has reduced its CO2 emissions by a third (since 2010). \n
        * It has also minimised packaging and optimised its transport routes.""")

def charge_data(): 
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    
    if uploaded_file is not None: 
        global dataset  # Notice how we make the variable global to be accessible outside of the function!! Now it is not local
        dataset = pd.read_csv(uploaded_file, parse_dates=["Order Date"])
        dataset["Order Date Year"] = dataset["Order Date"].dt.strftime('%Y')
                
        if st.button("See data"):
            st.markdown("<h3 style='text-align: center; color: red;'>DataFrame (2013 - 2016)</h3>", unsafe_allow_html=True)
            st.dataframe(dataset)
            pivot_table = pd.pivot_table(dataset, values="Sales", columns="Region", index="Order Date Year", aggfunc="sum").copy()
            st.markdown("<p style='text-align: center;'>Total sales per state (2013 - 2016)</p>", unsafe_allow_html=True)
            
            st.line_chart(pivot_table)
            st.balloons()
            st.snow()
            my_path = os.path.join("data", "animation.json")
            with open(my_path) as source:
                animation = json.load(source)
            st_lottie(animation, height=100, width=100)

def sales_cat_table():

    #Sales table per category
    dataset_sales = pd.DataFrame(dataset.groupby("Category")["Sales"].sum())
    
    dataset_sales ["Percentage"] = ((dataset_sales ["Sales"] /dataset_sales ["Sales"].sum())*100).round(2)
    dataset_sales ["Percentage"] = dataset_sales ["Percentage"].astype(str) + " %"  
    dataset_sales ["Sales"] = dataset_sales ["Sales"].astype("int")
    
    st.table(dataset_sales)
    return dataset_sales

def sales_cat_barplot():

    df_sales_cat = dataset.groupby(["Order Date Year","Category"])["Sales"].sum().reset_index()
    
    # bar plot    
    fig1 = px.bar(df_sales_cat, 
              x="Order Date Year",
              y = "Sales",
             color='Category',
             labels={"Order Date Year":''},
             color_discrete_sequence = px.colors.qualitative.Antique,
             height=500, 
             width=600)

    fig1.update_layout(font=dict(size=9),title_text="Sales of items per category and year")

    return fig1

def sales_subcat_barplot():

    dataset_subcat = dataset.groupby(["Order Date Year", "Category", "Sub-Category"])["Sales"].sum().reset_index()
    
    year = st.slider('Please, select a year', 2013, 2016)
    
    if year == 2013:
        data = dataset_subcat[dataset_subcat["Order Date Year"] == "2013"]
    elif year == 2014:
        data = dataset_subcat[dataset_subcat["Order Date Year"] == "2014"]
    elif year == 2015:
        data = dataset_subcat[dataset_subcat["Order Date Year"] == "2015"]
    else:
        data = dataset_subcat[dataset_subcat["Order Date Year"] == "2016"]
    
    # bar plot

    fig2 = px.bar(data, 
              x="Sub-Category",
              y = "Sales",
             color='Category',
             template="plotly_white",
             labels={"Order Date Year":'',"Sub-Category":" "},
             color_discrete_sequence = px.colors.qualitative.Antique,
             height=500, 
             width=600,
             title = "Sales per Sub-category year "+ str(year))

    fig2.update_layout(font=dict(size=20))

    return fig2


def sales_subcat_lc():
    
    dataset_order_date_subcat = dataset.groupby(["Order Date Year", "Sub-Category"])["Sales"].sum().reset_index()
    
    year = st.slider('Which years do you want to select?', 2013, 2016,(2013, 2016))
    
    with st.sidebar:
        sub_category = st.multiselect('Choose the Sub-Category', ['Paper', 'Labels', 'Storage', 'Binders', 'Art', 'Chairs', 'Phones',
       'Fasteners', 'Furnishings', 'Accessories', 'Envelopes',
       'Bookcases', 'Appliances', 'Tables', 'Supplies', 'Machines',
       'Copiers'], ['Paper', 'Labels', 'Storage', 'Binders', 'Art', 'Chairs', 'Phones',
       'Fasteners', 'Furnishings', 'Accessories', 'Envelopes',
       'Bookcases', 'Appliances', 'Tables', 'Supplies', 'Machines',
       'Copiers'])
    
    #line chart
    list_columns = []
    if year[0] != year[1]:
        if sub_category != []:
            
            for i in range(len(sub_category)):
                list_columns.append(sub_category[i])
                
            st.subheader("Sales of sub-category per year")
            df_sub_categ_mask = dataset_order_date_subcat[dataset_order_date_subcat["Sub-Category"].isin(list_columns)]
                        
            fig3 = px.line(df_sub_categ_mask[df_sub_categ_mask["Order Date Year"].isin([str(x) for x in np.arange(year[0], year[1] + 1)])],
                           x = "Order Date Year",
                           y = "Sales",
                           color= "Sub-Category",
                           labels={"Order Date Year":'',"Sub-Category":" "},
                           title='Sales Sub-Category year',
                           height=700, 
                            width=700,
                            markers=True
            )
            return fig3
        else: 
            return 2
    else:
        return 1 
    

def sales_state():
    my_path3 = os.path.join("data","statelatlong.csv")
    df_cities = pd.read_csv(my_path3)
    dataset2 = dataset.copy()
    dataset2["Order Date Year"] = dataset2["Order Date"].dt.year
    df_map = dataset2.groupby(["State", "Order Date Year"])[["Sales"]].sum().reset_index().merge(df_cities, left_on="State", right_on="City").drop(columns=["State_y", "City"]).rename(columns={"State_x":"State"})

    years =[2013, 2014, 2015, 2016]
    sell_year = st.selectbox('Choose the year', years)
    if sell_year in years:   
        year_to_show = sell_year
    
    view = pdk.ViewState(latitude=37, longitude=-95, zoom=3,)
    
    tooltip = {
        "html":
            "<b>State:</b> {State} <br/>"
            "<b>Sales:</b> {Sales} <br/>",
        "style": {
            "backgroundColor": "steelblue",
            "color": "black",
        }
    }
    salesLayer = pdk.Layer(
            type= "ScatterplotLayer",
            data=df_map,
            pickable=True,
            opacity=0.3,
            filled=True,
            onClick=True,
            radius_scale=10,
            radius_min_pixels=0,
            radius_max_pixels=30,
            line_width_min_pixels=1,
            get_position=["Longitude", "Latitude"],
            get_radius="Sales",
            get_fill_color=[252, 136, 3],
            get_line_color=[255,0,0],
        )

    r = pdk.Deck(
        layers=[salesLayer],
        initial_view_state=view,
        map_style="mapbox://styles/mapbox/light-v10",
        tooltip=tooltip,
    )
    map = st.pydeck_chart(r)
    salesLayer.data = df_map[df_map['Order Date Year'] == year_to_show]
  
    r.update()
    map.pydeck_chart(r)