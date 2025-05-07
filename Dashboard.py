import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from datetime import datetime

# ——————————————————————————————————————
# 1) Autenticación con Google Sheets (añadiendo scope de Drive)
# ——————————————————————————————————————
creds_info = st.secrets["google_sheets_credentials"]
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly"
]
credentials = service_account.Credentials.from_service_account_info(
    creds_info,
    scopes=SCOPES
)
gc = gspread.authorize(credentials)

# ——————————————————————————————————————
# 2) Funciones de acceso a datos
# ——————————————————————————————————————
SPREADSHEET_ID = "1mVVYxXd3vR2Ft9BD0QqWDD3_k87C3pHgeqI63gHEkJA"

def load_df(ws_name: str) -> pd.DataFrame:
    """Carga toda la hoja ws_name del spreadsheet indicado por ID."""
    sh = gc.open_by_key(SPREADSHEET_ID)
    ws = sh.worksheet(ws_name)
    return pd.DataFrame(ws.get_all_records())

def append_row(ws_name: str, row: list):
    """Agrega una fila al final de la hoja ws_name."""
    sh = gc.open_by_key(SPREADSHEET_ID)
    ws = sh.worksheet(ws_name)
    ws.append_row(row, value_input_option="USER_ENTERED")


# ——————————————————————————————————————
# 3) Lógica de cálculo
# ——————————————————————————————————————
def calcular_ganancia(precio_venta, precio_costo, cantidad, incluye_iva, pago_tarjeta):
    total_venta = round(precio_venta * cantidad, 4)
    total_costo = round(precio_costo * cantidad, 4)
    sat = round(total_venta * 0.16, 4) if incluye_iva else 0
    comision = round(total_venta * 0.036 * 1.16, 4) if pago_tarjeta else 0
    ganancia = round(total_venta - total_costo - sat - comision, 4)
    reserva = round(ganancia * 0.20, 4)
    iglesia = 0
    reyna = round(ganancia * 0.05, 4)
    paul = round(ganancia - reserva - iglesia - reyna, 4)
    return total_venta, total_costo, sat, comision, ganancia, reserva, iglesia, reyna, paul


# ——————————————————————————————————————
# 4) Registro de ventas
# ——————————————————————————————————————
def registrar_venta(producto, presentacion, cantidad,
                    precio_venta, precio_costo, incluye_iva, pago_tarjeta):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tv, tc, sat, com, gan, res, igl, rey, pau = calcular_ganancia(
        precio_venta, precio_costo, cantidad, incluye_iva, pago_tarjeta
    )
    fila = [
        fecha, producto, presentacion, incluye_iva, pago_tarjeta,
        cantidad, precio_venta, precio_costo, tv, tc, gan,
        res, igl, rey, pau, sat
    ]
    append_row("Ventas", fila)
    st.success("✅ Venta registrada en Google Sheets")


# ——————————————————————————————————————
# 5) Interfaz Streamlit
# ——————————————————————————————————————
def main():
    st.title("📊 Sistema de Ventas – ROCA VIVA / FZClean")

    linea = st.selectbox("Línea de productos", ["Roca Viva (RV)", "FZClean (FZ)"])

    precios_df = load_df("Precio Venta")
    costos_df  = load_df("Costos")

    # Selección de producto
    producto = st.selectbox("Producto", precios_df["Producto"].unique())
    pres = [c for c in precios_df.columns if c != "Producto"]
    presentacion = st.selectbox("Presentación", pres)

    cantidad = st.number_input("Cantidad", min_value=1.0, step=1.0, value=1.0)
    incluye_iva = st.checkbox("¿Precio incluye IVA?", value=True)
    pago_tarjeta = st.checkbox("¿Pago con tarjeta?", value=False)

    precio_venta = float(
        precios_df.loc[precios_df["Producto"] == producto, presentacion].iloc[0]
    )
    precio_costo = float(
        costos_df.loc[costos_df["Producto"] == producto, presentacion].iloc[0]
    )

    st.markdown(f"**Precio venta:** {precio_venta} — **Costo unitario:** {precio_costo}")

    if st.button("🖊️ Registrar venta"):
        registrar_venta(producto, presentacion, cantidad,
                        precio_venta, precio_costo, incluye_iva, pago_tarjeta)

    # Sidebar con Inventario y Egresos
    st.sidebar.title("📦 Inventario")
    st.sidebar.dataframe(load_df("Inventario"))

    st.sidebar.title("💸 Egresos")
    st.sidebar.dataframe(load_df("Egresos"))


if __name__ == "__main__":
    main()

