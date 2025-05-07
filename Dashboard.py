import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from datetime import datetime
from gspread.exceptions import GSpreadException

# ——————————————————————————————————————
# 1) Autenticación con Google Sheets
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
SPREADSHEET_ID = "1mVVYxXd3vR2Ft9BD0QqWDD3_k87C3pHgeqI63gHEkJA"

# ——————————————————————————————————————
# 2) Helpers de acceso a datos
# ——————————————————————————————————————
def list_worksheets():
    sh = gc.open_by_key(SPREADSHEET_ID)
    return [ws.title for ws in sh.worksheets()]

def load_df(ws_name: str) -> pd.DataFrame:
    """Carga ws_name en un DataFrame usando get_all_values()."""
    try:
        sh = gc.open_by_key(SPREADSHEET_ID)
        ws = sh.worksheet(ws_name)
    except GSpreadException:
        st.error(
            f"❌ No encontré la pestaña '{ws_name}'.\n"
            f"Las pestañas disponibles son:\n  • " + "\n  • ".join(list_worksheets())
        )
        st.stop()

    values = ws.get_all_values()
    if not values or len(values) < 1:
        st.error(f"❌ La pestaña '{ws_name}' está vacía.")
        st.stop()

    header = values[0]
    rows   = values[1:]
    df = pd.DataFrame(rows, columns=header)
    return df

def append_row(ws_name: str, row: list):
    """Añade una fila al final de ws_name."""
    try:
        sh = gc.open_by_key(SPREADSHEET_ID)
        ws = sh.worksheet(ws_name)
    except GSpreadException:
        st.error(
            f"❌ No encontré la pestaña '{ws_name}' para escribir.\n"
            f"Las pestañas disponibles son:\n  • " + "\n  • ".join(list_worksheets())
        )
        st.stop()
    ws.append_row(row, value_input_option="USER_ENTERED")

# ——————————————————————————————————————
# 3) Lógica de cálculo de venta y distribución
# ——————————————————————————————————————
def calcular_ganancia(precio_venta, precio_costo, cantidad, incluye_iva, pago_tarjeta):
    total_venta = round(precio_venta * cantidad, 4)
    total_costo = round(precio_costo  * cantidad, 4)
    sat         = round(total_venta * 0.16, 4) if incluye_iva else 0
    comision    = round(total_venta * 0.036 * 1.16, 4) if pago_tarjeta else 0
    ganancia    = round(total_venta - total_costo - sat - comision, 4)
    reserva     = round(ganancia * 0.20, 4)
    iglesia     = 0
    reyna       = round(ganancia * 0.05, 4)
    paul        = round(ganancia - reserva - iglesia - reyna, 4)
    return total_venta, total_costo, sat, comision, ganancia, reserva, iglesia, reyna, paul

# ——————————————————————————————————————
# 4) Registrar venta en la pestaña "Ventas"
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
# 5) App principal de Streamlit
# ——————————————————————————————————————
def main():
    st.title("📊 Sistema de Ventas – ROCA VIVA / FZClean")

    # 5.1 Línea de productos
    linea = st.selectbox("Línea de productos", ["Roca Viva (RV)", "FZClean (FZ)"])

    # 5.2 Carga precios y costos
    precios_df = load_df("Precio Venta")
    costos_df  = load_df("Costos")

    # 5.3 Selección de producto y presentación
    producto      = st.selectbox("Producto", precios_df["Producto"].unique())
    presentaciones = [c for c in precios_df.columns if c != "Producto"]
    presentacion  = st.selectbox("Presentación", presentaciones)

    # 5.4 Parámetros
    cantidad     = st.number_input("Cantidad", min_value=1.0, step=1.0, value=1.0)
    incluye_iva  = st.checkbox("¿Precio incluye IVA?", value=True)
    pago_tarjeta = st.checkbox("¿Pago con tarjeta?", value=False)

    # 5.5 Obtén precios desde los DataFrames
    precio_venta = float(precios_df.loc[precios_df["Producto"] == producto, presentacion].iloc[0])
    precio_costo = float(costos_df.loc[costos_df["Producto"] == producto, presentacion].iloc[0])

    st.markdown(f"**Precio venta:** {precio_venta} — **Costo unitario:** {precio_costo}")

    # 5.6 Registrar venta
    if st.button("🖊️ Registrar venta"):
        registrar_venta(
            producto, presentacion, cantidad,
            precio_venta, precio_costo,
            incluye_iva, pago_tarjeta
        )

    # 5.7 Sidebar: Inventario y Egresos
    st.sidebar.title("📦 Inventario")
    st.sidebar.dataframe(load_df("Inventario"))
    st.sidebar.title("💸 Egresos")
    st.sidebar.dataframe(load_df("Egresos"))


if __name__ == "__main__":
    main()



