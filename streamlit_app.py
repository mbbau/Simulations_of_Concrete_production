#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objs as go

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
# Header
    
header1, header2 = st.columns((1,6))

with header1:
    st.image('Brain Technology_Full color.png')

with header2:
    st.header('Concrete Production Dashboard',divider = "rainbow")


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

    driver_ranking =(fact_viajes[['chofer_id', 'cantidad','horas_viaje']]
                     .groupby('chofer_id')
                     .sum()
                     .reset_index()                     
    )
    driver_ranking = driver_ranking.join(dim_choferes, lsuffix="", rsuffix="_dim")
    driver_ranking['m3/hora'] = driver_ranking.cantidad / driver_ranking.horas_viaje
    driver_ranking = driver_ranking[['Nombre', 'eficiencia', 'm3/hora']]
    driver_ranking['rendimiento'] = round(driver_ranking.eficiencia * driver_ranking['m3/hora'],2)

    st.dataframe(driver_ranking,
                 column_order = ('Nombre', 'rendimiento'),
                 hide_index = True,
                 width = 20000,
                 column_config={
                     'Nombre': st.column_config.TextColumn("Chofer",),
                     'rendimiento': st.column_config.ProgressColumn("m3/hora",
                                                                 format="%f", 
                                                                 min_value=0,
                                                                 max_value = max(driver_ranking['rendimiento']),
                                                                 )
                 }
                 )
st.header('',divider = "rainbow")

familias_count = fact_viajes[['formula']]
familias_count.rename(columns={"formula": "formula_id"}, inplace=True)
dim_formulas.formula_id = dim_formulas.formula_id.astype('Int64')
familias_count = familias_count.merge(dim_formulas[['formula_id', 'Especificada']], on='formula_id', how='left')

familias_count = (
    familias_count
    .groupby('Especificada')
    .count()
    .reset_index()
)

familias_count['Especificada'] = familias_count['Especificada'].astype('category')

distribucion, reclamos = st.columns(2)

with distribucion:
    bar_chart = px.bar(familias_count, x= 'formula_id', y = 'Especificada', text_auto= True)
    bar_chart.update_layout(title={'text': 'Distribución de metros cúbicos despchados por familia', 'font': {'size': 20}},
                            xaxis_title='Cantidad de metros cúbicos despachados', 
                            yaxis_title='Familia de Hormigones',
                            yaxis = {'categoryorder':'total descending'})
    bar_chart.update_yaxes(type='category')

    st.plotly_chart(bar_chart)

with reclamos:
    conteo_reclamos = (
        fact_reclamos
        .groupby('tipo')
        .count()
        .reset_index()
    )
    bar_chart_reclamos = px.bar(conteo_reclamos, x= 'tipo', y = 'remito', text_auto= True)
    bar_chart_reclamos.update_layout(title={'text': 'Distribución de Reclamos', 'font': {'size': 20}},
                            xaxis_title='Tipo de Reclamo', 
                            yaxis_title='Conteo',
                            yaxis = {'categoryorder':'total descending'})
    bar_chart_reclamos.update_yaxes(type='category')

    st.plotly_chart(bar_chart_reclamos)
    

st.header('',divider = "rainbow")
##############################
# Quality control charts
for familia in fact_calidad['especificada'].unique():
    df_familia = fact_calidad[fact_calidad['especificada'] == familia]

    # Calcular la media y los límites de control
    media = df_familia['resistencia_28'].mean()
    desviacion_std = df_familia['resistencia_28'].std()
    lcl = media - 1.96*desviacion_std  # Límite de control inferior
    ucl = media + 1.96*desviacion_std  # Límite de control superior
    df_familia = df_familia.join(fact_viajes[['remito', 'fecha']], lsuffix="", rsuffix="_dim")
    
    df_familia_promedio_mensual =(df_familia[['fecha', 'resistencia_28']]
                                  .set_index('fecha')
                                  .resample('M')
                                  .mean()
    )

    
    # Crear el gráfico
    fig = px.scatter(df_familia, x='fecha', y='resistencia_28', hover_data='remito')

    fig.update_layout(title={'text': f'Control para la Familia de Resistencia: {familia}', 'y':0.9, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top', 'font': {'size': 24}})

    # Añadir líneas de media y límites de control
    fig.add_hline(y=media, line_dash="dash", line_color="green", annotation_text="Media")
    fig.add_hline(y=lcl, line_dash="dash", line_color="red", annotation_text="LCL")
    fig.add_hline(y=ucl, line_dash="dash", line_color="red", annotation_text="UCL")

    # Actualizar título y ejes
    fig.update_layout(xaxis_title='Observación', yaxis_title='Medición')

    fig2 = px.line(df_familia_promedio_mensual, x=df_familia_promedio_mensual.index, y='resistencia_28')
    fig2.update_layout(title={'text': f'Promedio mensual para la Familia de Resistencia: {familia}', 'y':0.9, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top', 'font': {'size': 24}})

    # Añadir líneas de media y límites de control
    fig2.add_hline(y=media, line_dash="dash", line_color="green", annotation_text="Media")
    #fig2.add_hline(y=lcl, line_dash="dash", line_color="red", annotation_text="LCL")
    #fig2.add_hline(y=ucl, line_dash="dash", line_color="red", annotation_text="UCL")


    st.plotly_chart(fig, use_container_width=True)
    st.plotly_chart(fig2, use_container_width=True)
    st.header('',divider = "rainbow")