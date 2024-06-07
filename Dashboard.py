import streamlit as st

# Configurar el layout de la página a "wide"
st.set_page_config(layout="wide")

# Función para el login
def check_login(username, password):
    return username == "prueba" and password == "prueba123"

# Verificar si el usuario ha iniciado sesión
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Página de Login
def login_page():
    st.subheader("Iniciar Sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Login"):
        if check_login(username, password):
            st.success("Login exitoso")
            st.session_state.logged_in = True
            st.experimental_rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

# Página de Bancos
def bancos_page():
    st.title('Sistema de Videovigilancia para Bancos')

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
        import pandas as pd
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
    st.title('Sistema de Videovigilancia para Plantas')

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
            {"hora": "12:30 AM", "detalle": "Colaborador en área peligrosa sin lentes de seguridad"},
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
        st.button('Botón pendiente')

    # Sección de registro de incidentes
    st.subheader('Registro de Incidentes')
    st.write("Historial de todos los incidentes detectados y las acciones tomadas.")

    # Ejemplo de registro de incidentes
    incidentes = [
            {"hora": "11:30 AM", "detalle": "Trabajador no tiene el equipo en el área de trabajo"},
            {"hora": "11:45 AM", "detalle": "Violación de distancia sin equipo de seguridad"},
            {"hora": "12:30 AM", "detalle": "Colaborador en área peligrosa sin lentes de seguridad"},
        ]

    # Opción para descargar el historial de incidentes
    st.sidebar.subheader("Descargar Historial")
    if st.sidebar.button("Descargar"):
        # Generar el archivo de historial de incidentes
        import pandas as pd
        df = pd.DataFrame(incidentes)
        df.to_csv("historial_incidentes.csv", index=False)
        st.sidebar.download_button(
            label="Descargar historial de incidentes",
            data=open("historial_incidentes.csv", "rb"),
            file_name="historial_incidentes.csv",
            mime="text/csv",
        )

# Menu lateral
if st.session_state.logged_in:
    st.sidebar.title("Menú")
    menu = st.sidebar.radio("Seleccione una opción", ["Bancos", "Plantas"])
    if menu == "Bancos":
        bancos_page()
    elif menu == "Plantas":
        plantas_page()
else:
    login_page()
