import streamlit as st
import pandas as pd
from google.oauth2 import service_account
import gspread

# Configuración de autenticación con Google Sheets
creds = service_account.Credentials.from_service_account_info({
    "type": "service_account",
    "project_id": "tribal-dispatch-459114-q0",
    "private_key_id": "8de35b0b17b2635ace5d4a7fdac54852be811d83",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDvLQj0iMAZHLTH\nBFaskM8UU95bMXEevkgIKGeMtltg2NVI14klXai8foZERLZQA9grd0LepgWIgKM0\nSbveDsJUoOfDpjWzBj0HGfFIhx428s/DXt/apAZ2KE4+Nhq8EwqkOHJaBW4jmMTa\niPWcIXpcMGYumDNi6ePVCeKMS6H2gtBukTml+cRKS8wD4lX8YHWdtf8BuuvJt0IZ\nRLBA3KAwarrU/HZpPtZo8cEPN5wUtgSXxct37PKz1maYNm3lBCk0h7HMyNZdRI/s\njtsT0FkozyYyHqgivAbsk4aKrAOrGZMqHClz7FQmwkd7vKROXfD0e7NDoTS4d0/o\nHTIVTsuvAgMBAAECggEAVJBcN7V4Egjrw+f9SzNB/EJw/lY7VC7b4gKDJiW9pj7U\nHlaSl4MHa2niyBVxTlYloqyemIEjuLEewxiE04ztWaWwfCTynJMKlc2u2UFoxe3Q\n1pdfV3siC7nRfD598lxbKVgJ2llMKUrU4x2ElYjireCw6C2JEaJ3mvXNQ2RkZfcI\nhpVslF3omcH9sZt7HRgh9yyJi0EcU9HqBk27lwY4Jb4iUOtzdeoEOMnaWH0rabWD\nqQP7Rn+Xodfy/U1kYxb1Kl0spLKSVnFKIIbImnlzErF8Vw9j9aAh9LPc+Esr3Hxe\nIkMHvnSZdsaJXioE5UM0XKd9cjDPkV3YDyBkifU0QQKBgQD5G/TeZvHxS6Kl9Zxq\nL2abvbmgy1MEcylMTQ0pgOa/4YpOwx9dpBpu8D5X5WgP+QIKMkdTi9VSwhJ74XP6\nWLKL7+/6dK2SY78VC4akEGSrPngvFp3AttT1oWGZBgjujxCop1eKVh4NtRXmkb77\nmsELPutNSP8jO0a4SIz37DkEQQKBgQD1yrygQTI0dA5tPL6t7kWoGZ4ykF++Z+RM\nANdqPMzQcCDQqWa+7FuG5luC0Ck/Xqkbt5GF65uNvlGyyS761letSLiKNXDcJRlb\ngSy0hwetZ9V7UD/62W0t0lY61KapCo3lB5BY/TL8DxHIFBt3SqZUuif5/7ZcWUM0\nG7doRAMT7wKBgQDFNa+uXhtN5o32CrJwkeQOia2qMS0gyba5FArGf6it4XToE6sC\nLAdNKl6AoTm3428M+W7kIkCYitGtRvfVCmEXTbVTNwmuac79bymBOwUnWIY26RWs\nWlHPv5oPVeq+SX5rtkckWjbirSiQZ3OlpocLSx1nCtIJZ0T+YVlQcK9WwQKBgQC9\nm1O/XAvaotyuL/n4OqLJdlmvL+hr/cEDUHLcpWJqONVXohZ8meBRREq7stDe7asO\nkqFT6djpkzN68++l2MtyBXM2SttxN71D9XYDHVcy0bLBmbqBTFEI1AVpBLo8FMQ5\nNYiI3WoDP6y756b4c0G0gpZsKHMI8mMBQ5BMgorNSQKBgQDVgrAzYrun36j/pCfI\nTk9/K7HmBIOwls8UGGze7VmLTpDnwI3SDM+N1siU8TpH5j/G+v13XIAzEtVhyalY\ndgZci0txM//YUsOfgMi6Rf9c3UivAXkiDn6IX3Qf4QwRJ8JsCh91sLUyZFM/yV3m\nQWLOECAakm3hk1H9zYgf/eEfUg==\n-----END PRIVATE KEY-----"
client_email = "roca-viva@tribal-dispatch-459114-q0.iam.gserviceaccount.com"
client_id = "100707975440794237472"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/roca-viva%40tribal-dispatch-459114-q0.iam.gserviceaccount.com"
})

# Conectar a Google Sheets
client = gspread.authorize(creds)

# Abrir la hoja de cálculo
sheet_name = "ROCA VIVA"  # Cambia al nombre exacto de tu hoja de cálculo en Google Sheets
sheet = client.open(sheet_name)
worksheet = sheet.get_worksheet(0)  # Cambia el índice si tienes varias hojas en tu documento

# Leer los datos de la hoja de Google Sheets en un DataFrame
data = worksheet.get_all_records()
df = pd.DataFrame(data)

# Función para mostrar los datos de la hoja de Google Sheets en Streamlit
def show_data():
    st.write(df)

# Cálculos de ventas y distribución
def calculate_sales_and_distribution(product, price, quantity, iva_inclusive, payment_method):
    # Aquí tomamos el precio y calculamos con IVA si es necesario
    if iva_inclusive:
        sale_price_without_iva = price / 1.16  # Si incluye IVA
    else:
        sale_price_without_iva = price
    
    # Calculamos la ganancia
    cost = df[df['Producto'] == product].iloc[0]['Costo unitario']  # Costo del producto
    total_sale = sale_price_without_iva * quantity
    total_profit = total_sale - cost * quantity
    
    # Distribución de ganancias
    company_reserve = total_profit * 0.20  # 20% para la empresa
    church = 0  # Iglesia tiene 0% por ahora
    reyna = total_profit * 0.05  # 5% para Reyna
    paul = total_profit - company_reserve - church - reyna  # El resto es para Paul

    # Descuento si se paga con tarjeta
    if payment_method == "Tarjeta":
        transaction_fee = total_sale * 0.036 * 1.16  # 3.6% de la venta + IVA sobre la comisión
        total_sale -= transaction_fee
    
    # Cálculos del SAT si corresponde
    if iva_inclusive:
        sat = total_sale * 0.16  # El 16% es para el SAT si se incluye IVA
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

# Interfaz de usuario para Streamlit
def main():
    st.title("Cálculo de Ventas y Distribución")
    st.subheader("Selecciona el producto y realiza el cálculo")

    # Seleccionar producto
    product = st.selectbox('Selecciona el producto:', df['Producto'].unique())

    # Ingresar precio, cantidad y otras opciones
    price = st.number_input('Precio de venta (sin IVA)', min_value=0.0, step=0.01)
    quantity = st.number_input('Cantidad de venta', min_value=1, step=1)
    iva_inclusive = st.checkbox('¿Incluye IVA?')
    payment_method = st.radio('Método de pago', ('Efectivo', 'Tarjeta'))

    # Botón para calcular
    if st.button('Calcular'):
        calculate_sales_and_distribution(product, price, quantity, iva_inclusive, payment_method)

if __name__ == '__main__':
    main()
