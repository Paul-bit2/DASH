import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from datetime import datetime

# ——————————————————————————————————————
# 1) Autenticación con Google Sheets
# ——————————————————————————————————————
# st.secrets["google_sheets_credentials"] ya es un dict, así que lo pasamos directamente:
creds_info = st.secrets["google_sheets_credentials"]
credentials = service_account.Credentials.from_service_account_info(
    creds_info,
    scopes=["https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"]
)
gc = gspread.authorize(credentials)


# ——————————————————————————————————————
# 2) Funciones de acceso a datos
# ——————————————————————————————————————
def load_df(sheet_name: str, ws_name: str) -> pd.DataFrame:
    """Carga toda la hoja ws_name de la spreadsheet sheet_name."""
    sh = gc.open(sheet_name)
    ws = sh.worksheet(ws_name)
    return pd.DataFrame(ws.get_all_records())

def append_row(sheet_name: str, ws_name: str, row: list):
    """Agrega una fila al final de la hoja ws_name."""
    sh = gc.open(sheet_name)
    ws = sh.worksheet(ws_name)
    ws.append_row(row)


# ——————————————————————————————————————
# 3) Lógica de cálculo
# ——————————————————————————————————————
def calcular_ganancia(precio_venta, precio_costo, cantidad, incluye_iva, pago_tarjeta):
    total_venta = round(precio_venta * cantidad, 4)
    total_costo = round(precio_costo * cantidad, 4)
    # SAT (16% del total si incluye IVA)
    sat = round(total_venta * 0.16, 4) if incluye_iva else 0
    # Comisión tarjeta (3.6% + IVA sobre la comisión)
    comision = round(total_venta * 0.036 * 1.16, 4) if pago_tarjeta else 0
    ganancia = round(total_venta - total_costo - sat - comision, 4)
    # Distribución: empresa 20%, iglesia 0%, Reyna 5%, Paul resto
    reserva = round(ganancia * 0.20, 4)
    iglesia = 0
    reyna = round(ganancia * 0.05, 4)
    paul = round(ganancia - reserva - iglesia - reyna, 4)
    return total_venta, total_costo, sat, comision, ganancia, reserva, iglesia, reyna, paul


# ——————————————————————————————————————
# 4) Registro de ventas
# ——————————————————————————————————————
def registrar_venta(sheet_name, fecha, producto, presentacion, cantidad,
                    precio_venta, precio_costo, incluye_iva, pago_tarjeta):
    tv, tc, sat, com, gan, res, igl, rey, pau = calcular_ganancia(
        precio_venta, precio_costo, cantidad, incluye_iva, pago_tarjeta
    )
    fila = [
        fecha, producto, presentacion, incluye_iva, pago_tarjeta,
        cantidad, precio_venta, precio_costo, tv, tc, gan,
        res, igl, rey, pau, sat
    ]
    append_row(sheet_name, "Ventas", fila)
    st.success("✅ Venta registrada en Google Sheets")


# ——————————————————————————————————————
# 5) App de Streamlit
# ——————————————————————————————————————
def main():
    st.title("📊 Sistema de Ventas – ROCA VIVA / FZClean")

    # 5.1 Elige línea
    linea = st.selectbox("Línea de productos", ["Roca Viva (RV)", "FZClean (FZ)"])

    # 5.2 Carga precios y costos
    SHEET = "ROCA VIVA"  # nombre de tu Google Sheets
    precios_df = load_df(SHEET, "Precio Venta")
    costos_df = load_df(SHEET, "Costos")

    # 5.3 Selección de producto y presentación
    df_linea = precios_df  # si quisieras filtrar por RV/FZ, lo harías aquí
    producto = st.selectbox("Producto", df_linea["Producto"].unique())
    presentaciones = [c for c in df_linea.columns if c != "Producto"]
    presentacion = st.selectbox("Presentación", presentaciones)

    # 5.4 Parámetros de la venta
    cantidad = st.number_input("Cantidad", min_value=1.0, step=1.0, value=1.0)
    incluye_iva = st.checkbox("¿Precio incluye IVA?", value=True)
    pago_tarjeta = st.checkbox("¿Pago con tarjeta?", value=False)

    # 5.5 Obtén precios desde los DataFrames
    precio_venta = float(
        df_linea.loc[df_linea["Producto"] == producto, presentacion].iloc[0]
    )
    precio_costo = float(
        costos_df.loc[costos_df["Producto"] == producto, presentacion].iloc[0]
    )

    # 5.6 Mostrar resumen antes de registrar
    st.markdown(f"**Precio venta:** {precio_venta} | **Costo unitario:** {precio_costo}")

    if st.button("🖊️ Registrar venta"):
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        registrar_venta(
            SHEET, fecha, producto, presentacion,
            cantidad, precio_venta, precio_costo,
            incluye_iva, pago_tarjeta
        )

    # 5.7 Panel lateral: inventario y egresos
    st.sidebar.title("📦 Inventario")
    inv_df = load_df(SHEET, "Inventario")
    st.sidebar.dataframe(inv_df)

    st.sidebar.title("💸 Egresos")
    eg_df = load_df(SHEET, "Egresos")
    st.sidebar.dataframe(eg_df)


if __name__ == "__main__":
    main()

