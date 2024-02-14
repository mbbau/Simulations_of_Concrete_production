import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="Concrete Quality Control",
    layout="wide"
    )

#######################
# Load data
fact_viajes = pd.read_csv('fact_viajes.csv')
fact_calidad = pd.read_csv('fact_calidad.csv')
fact_reclamos = pd.read_csv('fact_reclamos.csv')
dim_choferes = pd.read_csv('dim_choferes.csv')
dim_clientes = pd.read_csv('dim_clientes.csv')
dim_formulas = pd.read_csv('dim_formulas.csv')

fact_viajes['fecha'] = pd.to_datetime(fact_viajes['fecha'])
fact_viajes['Year'] = fact_viajes['fecha'].dt.strftime('%Y')
fact_viajes['Month'] = fact_viajes['fecha'].dt.strftime('%m')

columns = st.columns((0.2,0.8))

with columns[0]:
    st.title('Control de Calidad en el Hormigon')
    st.markdown('Cuando :blue[controlamos] la producción de una hormigonera, debemos observar que las muestras realmente pertenezcan a la :red[familia] para la que diseñamos, '
                'como así también que no haya :blue[señales] que nos indiquen que algo en el proceso ha cambiado. En esta aplicación web, mostraremos los dos enfoques '
                'mínimos que todo sistema de control debería tener.')


