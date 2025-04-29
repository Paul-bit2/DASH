import streamlit as st
import pandas as pd

# Cargar archivo Excel
archivo = 'calculadora.xlsx'

@st.cache_data
def cargar_datos():
    data = pd.read_excel(archivo, sheet_name='data')
    data['Producto'] = data['Producto'].fillna(method='ffill')  # Rellenar hacia abajo
    return data

data_df = cargar_datos()

st.title("Calculadora de Ingredientes")

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
        filtrado['Cantidad Necesaria (L)'] = filtrado['Cantidad (L)'] * factor
        filtrado = filtrado.drop(columns=['Cantidad (L)'])

        st.success("Cálculo completado. Resultados:")
        st.dataframe(filtrado, use_container_width=True)

