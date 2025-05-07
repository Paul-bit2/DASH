import streamlit as st
import pandas as pd
import numpy as np
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
    try:
        sh = gc.open_by_key(SPREADSHEET_ID)
        ws = sh.worksheet(ws_name)
        values = ws.get_all_values()
    except GSpreadException:
        st.error(
            f"❌ No pude abrir '{ws_name}'. Hojas disponibles:\n  • "
            + "\n  • ".join(list_worksheets())
        )
        st.stop()
    if not values or len(values) < 2:
        st.error(f"❌ La pestaña '{ws_name}' está vacía o sin datos.")
        st.stop()
    header, rows = values[0], values[1:]
    return pd.DataFrame(rows, columns=header)

def append_row(ws_name: str, row: list):
    try:
        sh = gc.open_by_key(SPREADSHEET_ID)
        ws = sh.worksheet(ws_name)
        ws.append_row(row, value_input_option="USER_ENTERED")
    except GSpreadException:
        st.error(
            f"❌ No pude escribir en '{ws_name}'. Hojas disponibles:\n  • "
            + "\n  • ".join(list_worksheets())
        )
        st.stop()

# ——————————————————————————————————————
# 3) Lógica de negocio
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
# 5) Páginas de la app
# ——————————————————————————————————————
def page_calculadora():
    st.header("🧪 Calculadora de Ingredientes")
    linea_choice = st.selectbox("Línea de productos", ["Roca Viva (RV)", "FZClean (FZ)"])
    if linea_choice == "Roca Viva (RV)":
        ws_recetas = "Recetas RV"
    else:
        ws_recetas = "Recetas FZ"
    df_rec = load_df(ws_recetas)
    # Expandir producto en filas
    df_rec["_Product"] = df_rec["Producto"].replace("", np.nan).ffill()
    productos = df_rec["_Product"].unique().tolist()
    st.subheader("Selecciona producto")
    producto = st.selectbox("Producto", productos)
    litros = st.number_input("Litros a preparar", min_value=1.0, step=1.0, value=1.0)
    if st.button("Calcular ingredientes"):
        sel = df_rec[df_rec["_Product"] == producto].copy()
        base_litros = float(sel["Cantidad (L)"].astype(float).iloc[0])
        factor = litros / base_litros
        sel["Cantidad Necesaria (L)"] = sel["Cantidad (L)"].astype(float) * factor
        st.dataframe(sel[["Ingrediente", "Cantidad Necesaria (L)"]])


def page_ventas():
    st.header("💰 Registrar Venta")
    precios_df = load_df("Precio Venta")
    costos_df = load_df("Costos")
    productos = precios_df["Producto"].unique().tolist()
    producto = st.selectbox("Producto", productos)
    pres = [c for c in precios_df.columns if c != "Producto" and c in costos_df.columns]
    presentacion = st.selectbox("Presentación", pres)
    cantidad = st.number_input("Cantidad", min_value=1.0, step=1.0, value=1.0)
    incluye_iva = st.checkbox("¿Precio incluye IVA?", value=True)
    pago_tarjeta = st.checkbox("¿Pago con tarjeta?", value=False)
    precio_venta = float(precios_df.loc[precios_df["Producto"] == producto, presentacion].iloc[0])
    precio_costo = float(costos_df.loc[costos_df["Producto"] == producto, presentacion].iloc[0])
    st.markdown(f"**Venta:** {precio_venta}   —   **Costo:** {precio_costo}")
    if st.button("Registrar Venta"):
        registrar_venta(producto, presentacion, cantidad,
                        precio_venta, precio_costo,
                        incluye_iva, pago_tarjeta)


def page_inventario():
    st.header("📦 Inventario")
    st.dataframe(load_df("Inventario"))


def page_egresos():
    st.header("💸 Egresos")
    st.dataframe(load_df("Egresos"))

# ——————————————————————————————————————
# 6) Menú principal
# ——————————————————————————————————————
def main():
    st.title("📊 Panel de Control – ROCA VIVA / FZClean")
    menu = st.sidebar.radio("Navegación", [
        "Calculadora", "Ventas", "Inventario", "Egresos"
    ])
    if menu == "Calculadora":
        page_calculadora()
    elif menu == "Ventas":
        page_ventas()
    elif menu == "Inventario":
        page_inventario()
    elif menu == "Egresos":
        page_egresos()

if __name__ == "__main__":
    main()



