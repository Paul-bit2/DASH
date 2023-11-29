import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(layout="wide")

# Función para cargar datos
@st.cache_data
def cargar_datos():
    df_dashboardruido = pd.read_csv('Dashboardruido.csv')
    df_dashboardnoruido = pd.read_csv('Dashboardnoruido.csv')
    df_dashboardgolpe = pd.read_csv('Dashboardgolpe.csv')
    df_anomaly = pd.read_csv('Dashboardanomaly.csv')
    return df_dashboardruido, df_dashboardnoruido, df_dashboardgolpe, df_anomaly

# Cargar los datos
df_dashboardruido, df_dashboardnoruido, df_dashboardgolpe, df_anomaly = cargar_datos()

# Convertir las columnas 'created_at' a datetime
for df in [df_dashboardruido, df_dashboardnoruido, df_dashboardgolpe, df_anomaly]:
    df['created_at'] = pd.to_datetime(df['created_at'])

# Crear gráficas con Plotly
def crear_grafica(df, x, y, title, height=300, color='#bd1408'):
    fig = px.line(df, x=x, y=y, title=title, line_shape='linear', render_mode='svg', line_dash_sequence=['solid'])
    fig.update_traces(line=dict(color=color))
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), autosize=True, height=height)
    fig.update_yaxes(title_text='Amperaje')
    return fig

# Selector de fecha para anomalías y lógica asociada
fecha_seleccionada = st.sidebar.date_input("Seleccionar Fecha para Anomalías", pd.to_datetime('2023-07-13').date())
unique_dates = df_anomaly['created_at'].dt.date.unique()
fig_anomalies = None
if fecha_seleccionada in unique_dates:
    current_day_data = df_anomaly[df_anomaly['created_at'].dt.date == fecha_seleccionada]
    first_anomaly = current_day_data[current_day_data['anomaly'] == -1].iloc[0]
    index_of_anomaly = current_day_data.index.get_loc(first_anomaly.name)
    start_index = max(0, index_of_anomaly - 15000)
    end_index = min(current_day_data.shape[0], index_of_anomaly + 15000)
    snippet = current_day_data.iloc[start_index:end_index]

    fig_anomalies = go.Figure()
    fig_anomalies.add_trace(go.Scatter(x=snippet['created_at'], y=snippet['l1'], mode='lines', name='L1', line=dict(color='black')))
    anomalies = snippet[snippet['anomaly'] == -1]
    fig_anomalies.add_trace(go.Scatter(x=anomalies['created_at'], y=anomalies['l1'], mode='markers', marker_color='red', name='Anomalía'))
    fig_anomalies.update_layout(title=f'Detección de Anomalías para el día {fecha_seleccionada}', xaxis_title='Tiempo', yaxis_title='Amperaje', height=300)

estado = st.sidebar.selectbox('Seleccionar Estado', [0, 1], key='estado_selector')
df_filtrado = df_dashboardgolpe[df_dashboardgolpe['estado'] == estado]

# Layout de Streamlit
st.markdown('<h1 style="text-align: center; font-family: \'Space Grotesk\'; font-size: 40px;margin-top: -80px; text-transform: uppercase;">Dashboard Detección de anomalías</h1>', unsafe_allow_html=True)
col1, col2, col3 = st.columns([2,2,2])

# Gráfica Ruido
with col1:
    fig_ruido = crear_grafica(df_dashboardruido, 'created_at', 'l1', 'Amperaje a través del tiempo (Ruido)', color='#bd1408')
    st.plotly_chart(fig_ruido, use_container_width=True)

# Gráfica No Ruido
with col2:
    fig_noruido = crear_grafica(df_dashboardnoruido, 'created_at', 'l1', 'Amperaje a través del tiempo (No Ruido)', color='black')
    st.plotly_chart(fig_noruido, use_container_width=True)

# Gráfica K-means (con control para estado)
with col3:
    fig_kmeans = crear_grafica(df_filtrado, 'created_at', 'l1', f'K-means Separación: Estado {estado}', color='#bd1408')
    st.plotly_chart(fig_kmeans, use_container_width=True)

col1, col2 = st.columns(2)

# Gráfica en la primera columna
with col2:
    st.markdown("""
        # ANOMALÍAS CONTADAS

        | FECHA       | NÚMERO DE ANOMALÍAS |
        | ----------- | ------------------- |
        | 2022-10-13  | 1,429,116           |
        | 2023-06-02  | 980,721             |
        | 2023-07-13  | 558,945             |
    """)

# Puedes colocar más contenido o gráficas en la segunda columna si lo deseas
with col1:
    if fig_anomalies:
        st.plotly_chart(fig_anomalies, use_container_width=True)
    else:
        st.write("No hay datos de anomalías para esta fecha.")






