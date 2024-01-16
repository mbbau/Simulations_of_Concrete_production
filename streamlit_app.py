#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import altair as alt


#######################
# Page configuration
st.set_page_config(
    page_title="Concrete Production Dashboard",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

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

#######################
# Sidebar
with st.sidebar:
    st.title('Filtering Panel')

#######################
# Header
    
header1, header2 = st.columns((1,6))

with header1:
    st.image('Brain Technology_Full color.png')

with header2:
    st.markdown('# Concrete Production Dashboard')


st.header("",divider = "rainbow")


#######################
# Main Dashboard 

def make_donut(input_text, input_response, input_color):
    if input_color == 'green':
      chart_color = ['#27AE60', '#12783D']
    if input_color == 'red':
      chart_color = ['#E74C3C', '#781F16']

    source = pd.DataFrame({
        "Topic": ["", input_text],
        "% value": [100-input_response, input_response]
    })
    source_bg = pd.DataFrame({
        "Topic":['', input_text],
        "% value": [100, 0]
    })
    plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
      theta="% value",
      color= alt.Color("Topic:N",
                      scale=alt.Scale(
                          #domain=['A', 'B'],
                          domain=[input_text, ''],
                          # range=['#29b5e8', '#155F7A']),  # 31333F
                          range=chart_color),
                      legend=None),
    ).properties(width=130, height=130)
    
    text = plot.mark_text(align='center', color="#29b5e8", font="Lato", fontSize=32, fontWeight=700, fontStyle="italic").encode(text=alt.value(f'{input_response} %'))
    
    plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
      theta="% value",
      color= alt.Color("Topic:N",
                      scale=alt.Scale(
                          # domain=['A', 'B'],
                          domain=[input_text, ''],
                          range=chart_color),  # 31333F
                      legend=None),
    ).properties(width=130, height=130)
    return plot_bg + plot + text

porcentaje_reclamos = round((len(fact_reclamos) / len(fact_viajes))*100, 0)
color_reclamos = "green" if porcentaje_reclamos <= 5 else "red"
porcentaje_viajes_con_reclamos = make_donut("% viajes con reclamos", porcentaje_reclamos, color_reclamos)

no_conforme = fact_calidad.loc[fact_calidad.especificada >= fact_calidad.resistencia_28]
porcentaje_resistencia = round((len(no_conforme) / len(fact_calidad))*100, 0)
color_conformidad = "green" if porcentaje_resistencia <= 10 else "red"
porcentaje_viajes_no_conformes = make_donut("% viajes no conformes", porcentaje_resistencia, color_conformidad)

a1, a2, a3 = st.columns((1.2, 4, 1.5), gap = 'small')

with a1:
    st.markdown('### Reclamos')
    st.altair_chart(porcentaje_viajes_con_reclamos)
    st.markdown('### No conformidades Resistencia')
    st.altair_chart(porcentaje_viajes_no_conformes)

with a2:
    st.markdown("### Producción en el tiempo")
    production = (fact_viajes
                  .set_index('fecha')
                  .cantidad
                  .resample('M')
                  .sum()
                  )
    production_over_time = px.line(production, x= production.index, y='cantidad')
    st.plotly_chart(production_over_time)

with a3:
    st.markdown("### Driver Ranking")

    driver_ranking =(fact_viajes[['chofer_id', 'cantidad']]
                     .groupby('chofer_id')
                     .sum()
                     .reset_index()                     
    )

    st.dataframe(driver_ranking,
                 column_order = ('chofer_id', 'cantidad'),
                 hide_index = True,
                 width = 20000,
                 column_config={
                     'chofer_id': st.column_config.TextColumn("Chofer",),
                     'cantidad': st.column_config.ProgressColumn("m3 Despachados",
                                                                 format="%f", 
                                                                 min_value=0,
                                                                 max_value = max(driver_ranking.cantidad),
                                                                 )
                 }
                 )




st.dataframe(production.head())

