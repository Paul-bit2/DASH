import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Establecer credenciales de Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('path_to_your_json_file.json', scope)  # Actualiza el path de tu archivo JSON
client = gspread.authorize(creds)

# Abrir la hoja de Google Sheets
sheet = client.open('NombreDeTuHojaDeGoogleSheets')  # Reemplaza con el nombre correcto de tu hoja
precio_venta_hoja = sheet.worksheet("Precio Venta")
costos_hoja = sheet.worksheet("Costos")
recetas_rv_hoja = sheet.worksheet("Recetas RV")
recetas_fz_hoja = sheet.worksheet("Recetas FZ")
inventario_hoja = sheet.worksheet("Inventario")
ventas_hoja = sheet.worksheet("Ventas")
egresos_hoja = sheet.worksheet("Egresos")

# Cargar datos desde Google Sheets
def cargar_datos(hoja):
    return pd.DataFrame(hoja.get_all_records())

# Cargar hojas en DataFrames
df_precio_venta = cargar_datos(precio_venta_hoja)
df_costos = cargar_datos(costos_hoja)
df_recetas_rv = cargar_datos(recetas_rv_hoja)
df_recetas_fz = cargar_datos(recetas_fz_hoja)
df_inventario = cargar_datos(inventario_hoja)
df_ventas = cargar_datos(ventas_hoja)
df_egresos = cargar_datos(egresos_hoja)

# Mostrar un selector para elegir entre RV y FZ
opcion = st.selectbox('Selecciona la gama de productos', ['Roca Viva (RV)', 'FZClean (FZ)'])

# Función para calcular el total y la venta
def calcular_venta(producto, cantidad, gama, pago_con_tarjeta=False):
    if gama == 'Roca Viva (RV)':
        # Buscar en la hoja de recetas RV
        precio = df_precio_venta[df_precio_venta['Producto'] == producto]['Rentas'].values[0]
        costo = df_costos[df_costos['Producto'] == producto]['Rentas'].values[0]
    else:
        # Buscar en la hoja de recetas FZ
        precio = df_precio_venta[df_precio_venta['Producto'] == producto]['Rentas'].values[0]
        costo = df_costos[df_costos['Producto'] == producto]['Rentas'].values[0]

    # Cálculo del total de venta
    total_venta = precio * cantidad
    total_costo = costo * cantidad

    # Cálculo de la ganancia
    ganancia = total_venta - total_costo

    # Si el pago es con tarjeta, se aplica el 3.6% + IVA sobre el total de la venta
    comision = 0
    if pago_con_tarjeta:
        comision = total_venta * 0.036  # 3.6% de comisión
        iva_comision = comision * 0.16  # IVA sobre la comisión
        comision += iva_comision  # Total comisión + IVA

    # Calcular el SAT si el precio incluye IVA
    sat = 0
    if "sí" in str(producto).lower():
        sat = total_venta * 0.16  # 16% de IVA si aplica

    # Regresar el total de venta, total de costo, ganancia, y la comisión
    return total_venta, total_costo, ganancia, comision, sat

# Función para calcular la distribución de ganancias
def calcular_distribucion(ganancia):
    reserva_empresa = ganancia * 0.20  # 20% para la reserva de la empresa
    reyna = ganancia * 0.15  # 15% para Reyna
    paul = ganancia * 0.65  # 65% para Paul
    return reserva_empresa, reyna, paul

# Interfaz de usuario en Streamlit
producto = st.selectbox('Selecciona el producto', df_precio_venta['Producto'].values)
cantidad = st.number_input('Cantidad a vender (en litros)', min_value=1, value=1)

# Opción para pago con tarjeta
pago_con_tarjeta = st.radio('¿El pago es con tarjeta?', ('No', 'Sí')) == 'Sí'

# Calcular los totales
if st.button('Calcular Venta'):
    total_venta, total_costo, ganancia, comision, sat = calcular_venta(producto, cantidad, opcion, pago_con_tarjeta)
    reserva_empresa, reyna, paul = calcular_distribucion(ganancia)

    st.write(f"Total Venta: ${total_venta}")
    st.write(f"Total Costo: ${total_costo}")
    st.write(f"Ganancia: ${ganancia}")
    st.write(f"Comisión (si aplica tarjeta): ${comision}")
    st.write(f"SAT (si aplica IVA): ${sat}")
    st.write(f"Distribución de ganancias:")
    st.write(f" - Reserva de la empresa: ${reserva_empresa}")
    st.write(f" - Reyna: ${reyna}")
    st.write(f" - Paul: ${paul}")

# Botón para registrar venta
if st.button('Registrar Venta'):
    fecha = pd.to_datetime('today').strftime('%Y-%m-%d')
    nueva_venta = [fecha, producto, cantidad, total_venta, total_costo, ganancia, reserva_empresa, reyna, paul, comision, sat]
    df_ventas.loc[len(df_ventas)] = nueva_venta
    # Actualiza la hoja de ventas en Google Sheets
    ventas_hoja.update([df_ventas.columns.values.tolist()] + df_ventas.values.tolist())
    st.write("Venta registrada correctamente.")

# Función para manejar la producción y revertir la acción
def manejar_produccion(producto, cantidad, gama, revertir=False):
    # Actualizar inventario y producción
    if revertir:
        # Restar del inventario lo producido
        df_inventario.loc[df_inventario['Producto'] == producto, 'Cantidad'] += cantidad
        st.write(f"Producción revertida para {producto}. El inventario ha sido restaurado.")
    else:
        # Descontar del inventario lo producido
        df_inventario.loc[df_inventario['Producto'] == producto, 'Cantidad'] -= cantidad
        st.write(f"Producción registrada para {producto}. El inventario ha sido actualizado.")

    # Actualizar Google Sheets
    inventario_hoja.update([df_inventario.columns.values.tolist()] + df_inventario.values.tolist())

# Botón para manejar la producción
if st.button('Registrar Producción'):
    manejar_produccion(producto, cantidad, opcion)

# Botón para revertir la producción
if st.button('Revertir Producción'):
    manejar_produccion(producto, cantidad, opcion, revertir=True)

# Función para mostrar inventario
st.write("Inventario de productos")
st.dataframe(df_inventario)

# Función para mostrar egresos
st.write("Egresos de la empresa")
st.dataframe(df_egresos)

