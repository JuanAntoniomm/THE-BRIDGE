import streamlit as st
import pickle
import os
from pathlib import Path

st.title('Mi modelo')

my_path = os.path.abspath('final_model.pkl')

mi_path = os.path.dirname(Path(__file__))
nombre_archivo = "final_model.pkl"
ruta_completa = os.path.join(mi_path, nombre_archivo)

with open(ruta_completa, "rb") as entrada:
    modelo = pickle.load(entrada)

x1 = st.slider("Introducir variable x1", 0., 1.,value=0.5, step=0.1)

x2 = st.slider("Introducir variable x2", 0., 1.,  value=0.5,step=0.1)

if st.button("Predecir con modelo"):
    st.metric("Que dice el modelo?", modelo.predict_proba([[x1,x2]])[:,1])
    
    
