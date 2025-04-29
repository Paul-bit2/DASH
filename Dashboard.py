import streamlit as st
import pandas as pd

# Cargar archivo Excel
archivo = 'calculadora.xlsx'

@st.cache_data
def cargar_datos():
    data = pd.read_excel(archivo, sheet_name='data')
    return data

data_df = cargar_datos()

st.title("Calculadora de Ingredientes")

# Obtener lista única de productos
productos = data_df['Producto'].dropna().unique()

producto_seleccionado = st.selectbox("Selecciona el producto:", productos)

litros = st.number_input("Cantidad de litros a preparar:", min_value=1.0, step=1.0)

if st.button("Calcular"):
    # Filtrar solo filas del producto seleccionado
    filtrado = data_df[data_df['Producto'] == producto_seleccionado]

    if filtrado.empty:
        st.warning("Producto no encontrado en la hoja 'data'.")
    else:
        factor = litros / 200.0

        filtrado = filtrado[['Ingrediente', 'Cantidad']].copy()
        filtrado['Cantidad Necesaria (L)'] = filtrado['Cantidad'] * factor
        filtrado = filtrado.drop(columns=['Cantidad'])

        st.success("Cálculo completado. Resultados:")
        st.dataframe(filtrado, use_container_width=True)
