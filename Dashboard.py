import streamlit as st
import pandas as pd
from PIL import Image

# Cargar archivo Excel
archivo = 'calculadora.xlsx'

@st.cache_data
def cargar_datos():
    data = pd.read_excel(archivo, sheet_name='data')
    data['Producto'] = data['Producto'].fillna(method='ffill')  # Rellenar hacia abajo
    return data

data_df = cargar_datos()

# Cargar imagen
imagen = Image.open("rocaviva.png")

# Crear una columna para imagen y título alineados
col1, col2 = st.columns([1, 5])
with col1:
    st.image(imagen, width=80)
with col2:
    st.markdown("<h1 style='margin-top: 10px;'>Calculadora</h1>", unsafe_allow_html=True)

st.markdown("""
<style>
    .resultado-tabla {
        background-color: #f9f9f9;
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 10px;
    }
    .stDataFrame {
        background-color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# Obtener lista única de productos
productos = data_df['Producto'].dropna().unique()

producto_seleccionado = st.selectbox("Selecciona el producto:", productos)

litros = st.number_input("Cantidad de litros a preparar:", min_value=1.0, step=1.0)

if st.button("Calcular"):
    # Filtrar solo filas del producto seleccionado y con ingrediente no vacío
    filtrado = data_df[(data_df['Producto'] == producto_seleccionado) & (data_df['Ingrediente'].notna())]

    if filtrado.empty:
        st.warning("Producto no encontrado o sin ingredientes válidos en la hoja 'data'.")
    else:
        factor = litros / 200.0

        filtrado = filtrado[['Ingrediente', 'Cantidad (L)']].copy()
        filtrado['Cantidad Necesaria'] = filtrado['Cantidad (L)'] * factor
        filtrado = filtrado.drop(columns=['Cantidad (L)'])

        # Convertir a mililitros si es menor a 1 litro
        def formatear_cantidad(x):
            if x < 1:
                return f"{round(x * 1000)} ml"
            else:
                return f"{round(x, 2)} L"

        filtrado['Cantidad Necesaria'] = filtrado['Cantidad Necesaria'].apply(formatear_cantidad)

        st.success("✅ Cálculo completado. Resultados:")
        with st.container():
            st.markdown('<div class="resultado-tabla">', unsafe_allow_html=True)
            st.dataframe(filtrado, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
