import streamlit as st
import gspread
from google.oauth2 import service_account
import pandas as pd
import numpy as np

# Autenticación con Google Sheets desde los secretos de Streamlit Cloud
def authenticate_with_google_sheets():
    creds = service_account.Credentials.from_service_account_info(
        st.secrets["google_sheets_credentials"]
    )
    client = gspread.authorize(creds)
    return client

# Cargar los datos desde una hoja específica de Google Sheets
def load_data_from_sheet(sheet_name, worksheet_name):
    client = authenticate_with_google_sheets()
    sheet = client.open(sheet_name)
    worksheet = sheet.worksheet(worksheet_name)
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    return df

# Función para realizar los cálculos de ganancias, distribución y más
def calcular_ganancia(precio_venta, precio_costo, cantidad, iva_incluido, pago_tarjeta):
    # Cálculos de totales
    total_venta = precio_venta * cantidad
    total_costo = precio_costo * cantidad

    # Cálculo de SAT si incluye IVA
    sat = 0
    if iva_incluido:
        sat = round(total_venta * 0.16, 4)  # 16% de IVA

    # Cálculo de comisión por tarjeta
    comision = 0
    if pago_tarjeta:
        comision = round(total_venta * 0.036 * 1.16, 4)  # 3.6% + IVA sobre la comisión

    # Ganancia
    ganancia = round(total_venta - total_costo - sat - comision, 4)

    # Distribución de ganancias
    reserva = round(ganancia * 0.2, 4)  # 20% para la reserva de la empresa
    iglesia = 0  # 0% para iglesia
    reyna = round(ganancia * 0.2, 4)  # 20% para Reyna
    paul = round(ganancia * 0.6, 4)  # 60% para Paul

    return total_venta, total_costo, sat, comision, ganancia, reserva, iglesia, reyna, paul

# Función para registrar una venta en Google Sheets
def registrar_venta(sheet_name, worksheet_name, fecha, producto, presentacion, cantidad, precio_venta, precio_costo, iva_incluido, pago_tarjeta):
    # Cálculos de ganancias
    total_venta, total_costo, sat, comision, ganancia, reserva, iglesia, reyna, paul = calcular_ganancia(precio_venta, precio_costo, cantidad, iva_incluido, pago_tarjeta)

    # Conexión a Google Sheets
    client = authenticate_with_google_sheets()
    sheet = client.open(sheet_name)
    worksheet = sheet.worksheet(worksheet_name)

    # Registrar los datos en Google Sheets
    worksheet.append_row([
        fecha, producto, presentacion, cantidad, precio_venta, precio_costo,
        total_venta, total_costo, ganancia, reserva, iglesia, reyna, paul, sat
    ])

    st.success("Venta registrada correctamente")

# Función para seleccionar productos
def seleccionar_producto(df):
    producto = st.selectbox("Selecciona un producto", df["Producto"].unique())
    return df[df["Producto"] == producto]

# Página principal de Streamlit
def main():
    st.title("Sistema de Gestión de Producción")

    # Selección de línea de productos (Roca Viva o FZClean)
    product_line = st.selectbox("Selecciona la línea de productos:", ("Roca Viva (RV)", "FZClean (FZ)"))

    # Cargar los productos y precios de Google Sheets según la línea seleccionada
    if product_line == "Roca Viva (RV)":
        sheet_name = "NombreDeTuHojaGoogleSheets"  # Cambia por el nombre de tu hoja en Google Sheets
        worksheet_name = "RV"  # Cambia por el nombre de la hoja que contiene los productos RV
    else:
        sheet_name = "NombreDeTuHojaGoogleSheets"  # Cambia por el nombre de tu hoja en Google Sheets
        worksheet_name = "FZ"  # Cambia por el nombre de la hoja que contiene los productos FZ

    # Cargar los datos desde Google Sheets
    df = load_data_from_sheet(sheet_name, worksheet_name)

    # Mostrar los productos disponibles
    st.write("Productos disponibles:", df)

    # Seleccionar un producto
    selected_product_data = seleccionar_producto(df)

    # Mostrar los detalles del producto seleccionado
    st.write("Detalles del producto seleccionado:", selected_product_data)

    # Ingresar la cantidad y precios
    cantidad = st.number_input("Cantidad a vender", min_value=1, step=1, value=1)
    iva_incluido = st.selectbox("¿Incluye IVA?", ("Sí", "No")) == "Sí"
    pago_tarjeta = st.selectbox("¿Pago con tarjeta?", ("Sí", "No")) == "Sí"

    # Asumir precios como ejemplo (estos pueden venir del DataFrame)
    precio_venta = selected_product_data["Precio de Venta"].values[0]  # Asegúrate de que el nombre de columna sea correcto
    precio_costo = selected_product_data["Costo"].values[0]  # Asegúrate de que el nombre de columna sea correcto

    # Calcular y mostrar los totales
    if st.button("Registrar Venta"):
        registrar_venta(sheet_name, worksheet_name, "2025-05-07", selected_product_data["Producto"].values[0],
                         "1 litro", cantidad, precio_venta, precio_costo, iva_incluido, pago_tarjeta)

    # Mostrar el total de las ganancias
    st.write(f"Precio de venta: {precio_venta}")
    st.write(f"Precio de costo: {precio_costo}")

if __name__ == "__main__":
    main()


