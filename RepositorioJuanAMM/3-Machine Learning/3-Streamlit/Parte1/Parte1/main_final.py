import streamlit as st
import functions as ft



## Basic setup and app layout

ft.config_page()

menu = st.sidebar.selectbox("Choose a section",("Overview",  "Upload your data", "Analyse sales"))

if menu == "Overview": 
    ft.home()

elif menu == "Upload your data":
    ft.charge_data()

else:
    sales_menu = st.sidebar.radio("Choose what you want to analyse",options=["Sales per category", "Sales per subcategory", "Sales per state"])

    if sales_menu == "Sales per category":

        st.header("Sales per category")

        table = ft.sales_cat_table()

        fig1 = ft.sales_cat_barplot()

        st.plotly_chart(fig1, width="stretch")

    elif sales_menu == "Sales per subcategory":

        st.header("Sales per subcategory of items")

        fig2 = ft.sales_subcat_barplot()

        st.plotly_chart(fig2,width="stretch")

        fig3 = ft.sales_subcat_lc()
        
        if fig3 == 1:
           st.write("Choose a range of years to filter")
        elif fig3 == 2:
            st.write("Choose the category/ies to filter")
        else:
            st.plotly_chart(fig3,width="stretch")

    else:
        ft.sales_state()