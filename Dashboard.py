import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import matplotlib.pyplot as plt

# Configurar el layout de la página a "wide"
st.set_page_config(page_title="Sistema de Videovigilancia", layout="wide")

# Página de Bancos
def bancos_page():
    # Título centrado
    st.markdown("<h1 style='text-align: center;'>Super Vision</h1>", unsafe_allow_html=True)
    # Sección de visualización de cámaras y alertas
    st.subheader('Cámaras en vivo y Alertas de Seguridad')
    col1, col2, col3 = st.columns([1, 1, 1.5])
    with col1:
        st.image("imagen2.jpg", caption="Cámara 1")
    with col2:
        st.image("imagen1.png", caption="Cámara 2")
    with col3:
        st.subheader('Alertas de Seguridad')
        alertas = [
            {"hora": "10:15 AM", "detalle": "Comportamiento sospechoso detectado en Cámara 1"},
            {"hora": "10:30 AM", "detalle": "Violación de distancia en Cámara 1"},
            {"hora": "11:00 AM", "detalle": "Comportamiento sospechoso detectado en Cámara 2"},
        ]

        for alerta in alertas:
            st.warning(f"{alerta['hora']}: {alerta['detalle']}")

    # Opciones de acciones
    st.subheader('Acciones Disponibles')
    col4, col5, col6 = st.columns(3)
    with col4:
        st.button('Revisar Grabaciones')
    with col5:
        st.button('Alertar a Seguridad')
    with col6:
        st.button('Llamar a Autoridades')

    # Sección de registro de incidentes
    st.subheader('Registro de Incidentes')
    st.write("Historial de todos los incidentes detectados y las acciones tomadas.")

    # Ejemplo de registro de incidentes
    incidentes = [
        {"hora": "10:15 AM", "detalle": "Comportamiento sospechoso en Cámara 1", "acción": "Alertado a Seguridad"},
        {"hora": "10:30 AM", "detalle": "Violación de distancia en Cámara 2", "acción": "Ninguna"},
        {"hora": "11:00 AM", "detalle": "Comportamiento sospechoso en Cámara 3", "acción": "Llamado a Autoridades"},
    ]

    for incidente in incidentes:
        st.info(f"{incidente['hora']}: {incidente['detalle']} - Acción: {incidente['acción']}")

    # Opción para descargar el historial de incidentes
    st.sidebar.subheader("Descargar Historial")
    if st.sidebar.button("Descargar"):
        # Generar el archivo de historial de incidentes
        df = pd.DataFrame(incidentes)
        df.to_csv("historial_incidentes.csv", index=False)
        st.sidebar.download_button(
            label="Descargar historial de incidentes",
            data=open("historial_incidentes.csv", "rb"),
            file_name="historial_incidentes.csv",
            mime="text/csv",
        )

# Página de Plantas
def plantas_page():
    # Título centrado
    st.markdown("<h1 style='text-align: center;'>Súper Visor: El Ojo del Futuro</h1>", unsafe_allow_html=True)

    # Sección de visualización de cámaras y alertas
    st.subheader('Cámaras en vivo y Alertas de Seguridad')
    col1, col2, col3 = st.columns([1, 1, 1.5])
    with col1:
        st.image("imagen4.png", caption="Cámara 1")
    with col2:
        st.image("imagen5.png", caption="Cámara 2")
    with col3:
        st.subheader('Alertas de Seguridad')
        alertas = [
            {"hora": "11:30 AM", "detalle": "Trabajador no tiene el equipo en el área de trabajo"},
            {"hora": "11:45 AM", "detalle": "Violación de distancia sin equipo de seguridad"},
            {"hora": "12:30 PM", "detalle": "Colaborador en área peligrosa sin lentes de seguridad"},
        ]

        for alerta in alertas:
            st.warning(f"{alerta['hora']}: {alerta['detalle']}")

    # Opciones de acciones
    st.subheader('Acciones Disponibles')
    col4, col5, col6 = st.columns(3)
    with col4:
        st.button('Revisar Grabaciones')
    with col5:
        st.button('Alertar a Seguridad')
    with col6:
        st.button('Llamar a Autoridades')

    # Sección de registro de incidentes
    st.subheader('Registro de Incidentes')
    st.write("Historial de todos los incidentes detectados y las acciones tomadas.")

    # Ejemplo de registro de incidentes
    incidentes = [
        {"hora": "11:30 AM", "detalle": "Trabajador no tiene el equipo en el área de trabajo",
         "acción": "Alertado a Seguridad"},
        {"hora": "11:45 AM", "detalle": "Violación de distancia sin equipo de seguridad", "acción": "Ninguna"},
        {"hora": "12:30 PM", "detalle": "Colaborador en área peligrosa sin lentes de seguridad",
         "acción": "Llamado a Autoridades"},
    ]

    for incidente in incidentes:
        st.info(f"{incidente['hora']}: {incidente['detalle']} - Acción: {incidente['acción']}")

    # Opción para descargar el historial de incidentes
    st.sidebar.subheader("Descargar Historial")
    if st.sidebar.button("Descargar"):
        # Generar el archivo de historial de incidentes
        df = pd.DataFrame(incidentes)
        df.to_csv("historial_incidentes.csv", index=False)
        st.sidebar.download_button(
            label="Descargar historial de incidentes",
            data=open("historial_incidentes.csv", "rb"),
            file_name="historial_incidentes.csv",
            mime="text/csv",
        )

# Página de Estadísticas
def estadisticas_page():
    # Título centrado
    st.markdown("<h1 style='text-align: center;'>Estadísticas de Incidentes</h1>", unsafe_allow_html=True)

    # Datos de ejemplo de alertas
    alertas = [
        {"hora": "10:15 AM", "detalle": "Comportamiento sospechoso detectado en Cámara 1"},
        {"hora": "10:30 AM", "detalle": "Violación de distancia en Cámara 1"},
        {"hora": "11:00 AM", "detalle": "Comportamiento sospechoso detectado en Cámara 2"},
        {"hora": "11:30 AM", "detalle": "Trabajador no tiene el equipo en el área de trabajo"},
        {"hora": "11:45 AM", "detalle": "Violación de distancia sin equipo de seguridad"},
        {"hora": "12:30 PM", "detalle": "Colaborador en área peligrosa sin lentes de seguridad"},
    ]

    alertas_df = pd.DataFrame(alertas)
    alertas_df['hora'] = pd.to_datetime(alertas_df['hora'], format='%I:%M %p')

    # Gráfica de incidentes por hora
    st.write("Gráfica de incidentes por hora")
    fig, ax = plt.subplots()
    alertas_df['hora'].dt.hour.value_counts().sort_index().plot(kind='bar', ax=ax)
    ax.set_xlabel('Hora del día')
    ax.set_ylabel('Número de incidentes')
    st.pyplot(fig)

    # Gráfica de incidentes por día de la semana (datos inventados)
    st.write("Gráfica de incidentes por día de la semana")
    dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
    incidentes_dias = [5, 3, 6, 2, 4]
    fig, ax = plt.subplots()
    ax.bar(dias_semana, incidentes_dias)
    ax.set_xlabel('Día de la semana')
    ax.set_ylabel('Número de incidentes')
    st.pyplot(fig)

# Menu lateral
with st.sidebar:
    selected_menu = option_menu("Menú", ["Bancos", "Plantas", "Estadísticas"],
                                icons=['building', 'factory', 'bar-chart'],
                                menu_icon="cast", default_index=0,
                                styles={
                                    "container": {"padding": "0!important", "background-color": "#fafafa"},
                                    "icon": {"color": "orange", "font-size": "25px"},
                                    "nav-link": {"font-size": "25px", "text-align": "left", "margin": "0px",
                                                 "--hover-color": "#eee"},
                                    "nav-link-selected": {"background-color": "#04297a"},
                                }
                                )
if selected_menu == "Bancos":
    bancos_page()
elif selected_menu == "Plantas":
    plantas_page()
elif selected_menu == "Estadísticas":
    estadisticas_page()
