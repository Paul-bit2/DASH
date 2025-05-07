import streamlit as st
import gspread
from google.oauth2 import service_account
import json

# Obtener las credenciales desde los secretos
creds = json.loads(st.secrets["google_sheets_credentials"])

# Autenticación con Google Sheets
credentials = service_account.Credentials.from_service_account_info(creds)
client = gspread.authorize(credentials)

# Conectar con la API de Google Sheets
client = gspread.authorize(creds)

# Obtener la hoja de trabajo
sheet_name = 'ROCA VIVA'  # El nombre de tu hoja de Google Sheets
worksheet = client.open(sheet_name).sheet1

# Función para obtener datos de la hoja de Google Sheets
def get_data_from_sheet():
    data = worksheet.get_all_records()
    return pd.DataFrame(data)

# Función para enviar los datos calculados de producción
def update_data_in_sheet(sheet_name, row, data):
    worksheet = client.open(sheet_name).sheet1
    worksheet.insert_row(data, row)  # Inserta los datos en una nueva fila

# Interfaz de usuario
def main():
    st.title("Cálculo de Ventas y Producción")
    st.subheader("Calculadora de ventas y distribución")

    # Cargar los datos de la hoja de Google Sheets
    df = get_data_from_sheet()

    # Mostrar los datos en Streamlit
    st.write("Datos de la hoja de Google Sheets:")
    st.dataframe(df)

    # Selección de producto y otros campos
    product = st.selectbox('Selecciona el producto', df['Producto'].unique())
    quantity = st.number_input('Cantidad de producción', min_value=1, step=1)
    iva_inclusive = st.checkbox('¿Incluye IVA?')
    payment_method = st.radio('Método de pago', ['Efectivo', 'Tarjeta'])

    # Botón de calcular
    if st.button('Calcular'):
        calculate_sales_and_distribution(product, quantity, iva_inclusive, payment_method)

# Cálculos de venta y distribución
def calculate_sales_and_distribution(product, quantity, iva_inclusive, payment_method):
    # Obtener el precio del producto seleccionado
    price = df[df['Producto'] == product]['Granel'].values[0]  # Asumiendo que usamos el precio "Granel"

    # Si el precio incluye IVA, lo restamos para calcular el precio sin IVA
    if iva_inclusive:
        price_without_iva = price / 1.16
    else:
        price_without_iva = price

    # Calcular total de la venta
    total_sale = price_without_iva * quantity

    # Cálculos de ganancias y distribución
    total_profit = total_sale - price * quantity
    company_reserve = total_profit * 0.20  # 20% para la empresa
    church = 0  # 0% para la iglesia
    reyna = total_profit * 0.05  # 5% para Reyna
    paul = total_profit - company_reserve - church - reyna  # El resto es para Paul

    # Descuento de tarjeta
    if payment_method == "Tarjeta":
        transaction_fee = total_sale * 0.036 * 1.16  # 3.6% más IVA
        total_sale -= transaction_fee

    # Calcular SAT
    if iva_inclusive:
        sat = total_sale * 0.16  # El 16% es para SAT si incluye IVA
    else:
        sat = 0

    # Mostrar resultados
    st.write(f"Total de venta: {total_sale}")
    st.write(f"Ganancia: {total_profit}")
    st.write(f"Reserva de empresa (20%): {company_reserve}")
    st.write(f"Reyna (5%): {reyna}")
    st.write(f"Paul: {paul}")
    st.write(f"SAT (16% si incluye IVA): {sat}")
    st.write(f"Total con impuestos: {total_sale - sat}")

if __name__ == '__main__':
    main()
