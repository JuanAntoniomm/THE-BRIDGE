import streamlit as st
import pickle
import numpy as np

st.title('Energy forecaster')

# Model load
with open("models/model_lgb.pkl", "rb") as f:
    model = pickle.load(f)

# Create tabs
tab1, tab2 = st.tabs(["Prediction", "About the model"])

with tab1:
    text_1 = """
<p style="text-align: justify;">
The price of electricity varies continuously depending on the energy mix available at any given time. 
Each type of generation contributes differently to the final market cost. 
\n In this tool, you can simulate the amount generated in a day in each of the six most influential sources using the sliders, and the predictive model will estimate
the price of electricity in €/MWh according to the chosen combination.
</p>
"""
    st.markdown(text_1, unsafe_allow_html=True)
    st.header("Enter the generation in one day (MWh)")

    col1, col2, col3 = st.columns([6, 6, 6])
    
    #	Fossil Gas	Hydro Pumped Storage.1	Nuclear	Waste	Fossil Oil	Fossil Hard coal
    
    with col1:
        fossil_gas = st.slider("Fossil Gas", 2_000.0, 15_300.0,  5_000.0, 10.0)
        hydro = st.slider("Hydro Pumped Storage.1", 36.0, 2_950.0, 1_050.0, 10.0)
        nuclear = st.slider("Nuclear", 11.0, 7_150.0, 6_000.0, 10.0)
            
    with col2:       
        waste = st.slider("Waste", 96.0, 310.0, 195.0, 10.0)
        fossil_oil = st.slider("Fossil Oil", 2.0, 92.0, 31.0, 10.0)
        fossil_hard_coal = st.slider("Fossil Hard coal", 0.0, 920.0, 290.0, 10.0)

    with col3:
        if st.button("Predict price €/MWh"):
            input_data = np.array([[fossil_gas, fossil_hard_coal, fossil_oil, hydro, nuclear, waste]])
            pred = model.predict(input_data)
            st.metric("Estimated price (€/MWh))", f"{pred[0]:.2f}")
    text_2 = """
    <p style="text-align: justify;">
    For the predictor to work best, the default value for each slider corresponds to the average daily generation of each source in the dataset
    used to train the model. 
    The maximum and minimum values correspond to the maximum and minimum generation recorded in a day for each source.
    </p>
    """            
    st.markdown(text_2, unsafe_allow_html=True)

with tab2:
    st.header("Project objective")

    text_3 = """
    <p style="text-align: justify;">
    The purpose of this project is to develop a regression model based on machine learning techniques that allows the 
    daily price of electricity to be estimated based on the available energy mix. This model was trained using historical data that
    includes:<br><br>
    - The contribution of each technology to the daily energy mix.<br>
    - Resulting price in the wholesale market.<br><br>
    The ultimate goal is to build a model capable of anticipating price behaviour, facilitating strategic decision-making
    and improving operational management within the market.
    </p>
    """
    st.markdown(text_3, unsafe_allow_html=True)

    st.header("Data used")
    text_4 = """
    <p style="text-align: justify;">
    The data used in this project comes from official sources. Specifically, from Red Eléctrica de España. The data has been downloaded from
    the REE API, which provides detailed information on electricity generation by source, demand and prices.
    Daily data has been collected to ensure adequate
    representativeness of the model.<br><br>   
    """
    st.markdown(text_4, unsafe_allow_html=True)

    st.header("About the model")
    text_5 = """
    <div style="line-height:1.4;">
      <p style="text-align: justify; margin-bottom: 0.6rem;">
        A Random Forest Regressor model was used to construct the predictor, selected for its ability to capture non-linear relationships and its good performance in complex prediction problems.
        The model was evaluated on a test set of 20% of the data, obtaining the following metrics: 
        The model was evaluated on a test set comprising 20% of the data, obtaining the following metrics:
      </p>

      <p style="text-align: justify; margin-top:0.2rem;">
        The main metrics are: 
        <span style="text-decoration: underline; font-weight:600;">R²</span>, 
        <span style="text-decoration: underline; font-weight:600;">MAE</span>, 
        <span style="text-decoration: underline; font-weight:600;">RMSE</span> y 
        <span style="text-decoration: underline; font-weight:600;">MAPE</span>.
      </p>

      <div style="margin-top:1rem; display:flex; justify-content:center;">
        <table style="border-collapse: collapse; width: 340px;">
          <thead>
            <tr>
              <th style="text-align: left; padding: 6px 10px; border-bottom: 2px solid #ddd;">Metric</th>
              <th style="text-align: right; padding: 6px 10px; border-bottom: 2px solid #ddd;">Value</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td style="padding: 6px 10px; border-bottom: 1px solid #f0f0f0;">R²</td>
              <td style="padding: 6px 10px; text-align: right; border-bottom: 1px solid #f0f0f0;">0.8657</td>
            </tr>
            <tr>
              <td style="padding: 6px 10px; border-bottom: 1px solid #f0f0f0;">MAE (€/MWh)</td>
              <td style="padding: 6px 10px; text-align: right; border-bottom: 1px solid #f0f0f0;">10.0763</td>
            </tr>
            <tr>
              <td style="padding: 6px 10px; border-bottom: 1px solid #f0f0f0;">RMSE (€/MWh)</td>
              <td style="padding: 6px 10px; text-align: right; border-bottom: 1px solid #f0f0f0;">14.1760</td>
            </tr>
            <tr>
              <td style="padding: 6px 10px;">MAPE</td>
              <td style="padding: 6px 10px; text-align: right;">27.5855%</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    """

    st.markdown(text_5, unsafe_allow_html=True)