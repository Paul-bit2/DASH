import time
from pathlib import Path

import streamlit as st
import pandas as pd
import numpy as np


# ============================================================
# 0) Debug utilities
# ============================================================
def _now():
    return time.perf_counter()

def _fmt_s(x: float) -> str:
    return f"{x:.3f}s"

def dbg(msg: str):
    if st.session_state.get("_debug_on", False):
        st.sidebar.write(msg)

def die(msg: str):
    st.error(msg)
    st.stop()


# ============================================================
# 1) Page config + debug panel
# ============================================================
st.set_page_config(page_title="Panel RV/FZ (Excel local)", layout="wide")

if "_runs" not in st.session_state:
    st.session_state["_runs"] = 0
st.session_state["_runs"] += 1

st.sidebar.markdown("## 🧰 Debug")
st.session_state["_debug_on"] = st.sidebar.checkbox("Mostrar debug", value=True)
st.sidebar.write("🔁 Reruns:", st.session_state["_runs"])

t_app = _now()
dbg("✅ Inicio Dashboard.py")


# ============================================================
# 2) Locate Excel file robustly
#    - Prefer: same directory as this script
#    - Fallback: repo root (current working directory)
# ============================================================
SCRIPT_DIR = Path(__file__).resolve().parent
EXCEL_CANDIDATES = [
    SCRIPT_DIR / "RV.xlsx",
    Path("RV.xlsx"),
    SCRIPT_DIR / "data" / "RV.xlsx",
    Path("data") / "RV.xlsx",
]

EXCEL_PATH = None
for p in EXCEL_CANDIDATES:
    if p.exists():
        EXCEL_PATH = p.resolve()
        break

dbg(f"📁 SCRIPT_DIR: {SCRIPT_DIR}")
dbg(f"📄 Excel encontrado: {EXCEL_PATH if EXCEL_PATH else 'NO'}")

with st.sidebar.expander("🔎 Diagnóstico de archivos"):
    st.write("Directorio actual (cwd):", str(Path.cwd()))
    st.write("Ruta del script:", str(Path(__file__).resolve()))
    st.write("Candidatos buscados:")
    for p in EXCEL_CANDIDATES:
        st.write("•", str(p), "=>", "✅" if p.exists() else "❌")

if EXCEL_PATH is None:
    die(
        "❌ No se encontró **RV.xlsx**.\n\n"
        "Soluciones:\n"
        "1) Sube `RV.xlsx` al repo.\n"
        "2) Ponlo en el mismo folder que `Dashboard.py`.\n"
        "3) O ponlo en `/data/RV.xlsx`.\n"
    )


# ============================================================
# 3) Open Excel once (cache_resource) + parse sheets (cache_data)
# ============================================================
@st.cache_resource
def get_excel_file(excel_path_str: str):
    # abrir estructura del Excel una sola vez
    return pd.ExcelFile(excel_path_str)

@st.cache_data(show_spinner=False)
def load_df(excel_path_str: str, ws_name: str) -> pd.DataFrame:
    xl = get_excel_file(excel_path_str)
    df = xl.parse(ws_name)
    if df is None or df.empty:
        return pd.DataFrame()
    df.columns = df.columns.astype(str).str.strip()
    # strip a strings
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    return df


# ============================================================
# 4) Excel diagnostics
# ============================================================
t0 = _now()
try:
    dbg("📥 Abriendo ExcelFile...")
    xl = get_excel_file(str(EXCEL_PATH))
    sheet_names = xl.sheet_names
    dbg(f"✅ Hojas: {sheet_names}")
    dbg(f"⏱️ ExcelFile abierto en {_fmt_s(_now() - t0)}")

except Exception as e:
    st.exception(e)
    die("❌ Error abriendo RV.xlsx (mira el stack trace arriba).")

with st.sidebar.expander("📚 Hojas detectadas"):
    st.write(sheet_names)

# Quick test read
with st.sidebar.expander("🧪 Test de lectura"):
    test_sheet = st.selectbox("Leer una hoja (prueba)", sheet_names, index=0)
    nrows = st.number_input("Filas a leer (prueba)", min_value=1, max_value=500, value=20, step=1)
    if st.button("Probar lectura"):
        try:
            t1 = _now()
            df_test = pd.read_excel(EXCEL_PATH, sheet_name=test_sheet, nrows=int(nrows))
            st.success(f"✅ Leído OK: {test_sheet} ({df_test.shape[0]}x{df_test.shape[1]}) en {_fmt_s(_now() - t1)}")
            st.dataframe(df_test, use_container_width=True)
        except Exception as e:
            st.exception(e)
            die("❌ Falló la lectura de prueba (mira el error arriba).")


# ============================================================
# 5) Business logic (solo lectura)
# ============================================================
def calcular_ganancia(precio_venta, precio_costo, cantidad, incluye_iva, pago_tarjeta):
    tv = round(precio_venta * cantidad, 4)
    tc = round(precio_costo * cantidad, 4)
    sat = round(tv * 0.16, 4) if incluye_iva else 0
    com = round(tv * 0.036 * 1.16, 4) if pago_tarjeta else 0
    gan = round(tv - tc - sat - com, 4)

    res = round(gan * 0.20, 4)
    igl = 0
    rey = round(gan * 0.05, 4)
    pau = round(gan - res - igl - rey, 4)
    return tv, tc, sat, com, gan, res, igl, rey, pau


# ============================================================
# 6) Pages
# ============================================================
def page_calculadora():
    st.header("🧪 Calculadora de Ingredientes (solo lectura)")

    linea = st.selectbox("Línea de productos", ["Roca Viva (RV)", "FZClean (FZ)"])
    ws_recetas = "Recetas RV" if "RV" in linea else "Recetas FZ"

    if ws_recetas not in sheet_names:
        die(f"❌ No existe la hoja '{ws_recetas}' en RV.xlsx")

    t = _now()
    df_rec = load_df(str(EXCEL_PATH), ws_recetas)
    dbg(f"📄 load_df({ws_recetas}) => {df_rec.shape} en {_fmt_s(_now() - t)}")

    if df_rec.empty:
        die(f"❌ La hoja '{ws_recetas}' está vacía.")

    req_cols = {"Producto", "Ingrediente", "Cantidad (L)"}
    missing = req_cols - set(df_rec.columns)
    if missing:
        die(f"❌ Faltan columnas en '{ws_recetas}': {', '.join(sorted(missing))}")

    df_rec["_Product"] = df_rec["Producto"].replace("", np.nan).ffill()
    productos = sorted(df_rec["_Product"].dropna().unique().tolist())
    producto = st.selectbox("Producto", productos)

    litros = st.number_input("Litros a preparar", min_value=1.0, step=1.0, value=200.0)

    if st.button("Calcular ingredientes"):
        sel = df_rec[df_rec["_Product"] == producto].copy()
        base_litros = 200.0
        factor = litros / base_litros

        sel["Cantidad (L)"] = pd.to_numeric(sel["Cantidad (L)"], errors="coerce").fillna(0.0)
        sel["Cantidad Necesaria (L)"] = sel["Cantidad (L)"] * factor

        st.dataframe(sel[["Ingrediente", "Cantidad Necesaria (L)"]], use_container_width=True)


def page_ventas():
    st.header("💰 Simulador de Venta (solo lectura)")

    for needed in ["Precio Venta", "Costos"]:
        if needed not in sheet_names:
            die(f"❌ No existe la hoja '{needed}' en RV.xlsx")

    t = _now()
    precios_df = load_df(str(EXCEL_PATH), "Precio Venta")
    dbg(f"📄 load_df(Precio Venta) => {precios_df.shape} en {_fmt_s(_now() - t)}")

    t = _now()
    costos_df = load_df(str(EXCEL_PATH), "Costos")
    dbg(f"📄 load_df(Costos) => {costos_df.shape} en {_fmt_s(_now() - t)}")

    if precios_df.empty or costos_df.empty:
        die("❌ 'Precio Venta' o 'Costos' está vacío.")

    if "Producto" not in precios_df.columns or "Producto" not in costos_df.columns:
        die("❌ Ambas hojas deben tener columna 'Producto'.")

    productos = sorted(precios_df["Producto"].dropna().unique().tolist())
    producto = st.selectbox("Producto", productos)

    pres = [c for c in precios_df.columns if c != "Producto" and c in costos_df.columns]
    if not pres:
        die("❌ No hay presentaciones coincidentes entre 'Precio Venta' y 'Costos'.")

    presentacion = st.selectbox("Presentación", pres)

    cantidad = st.number_input("Cantidad", min_value=1.0, step=1.0, value=1.0)
    incluye_iva = st.checkbox("¿Precio incluye IVA?", value=True)
    pago_tarjeta = st.checkbox("¿Pago con tarjeta?", value=False)

    try:
        pv_raw = precios_df.loc[precios_df["Producto"] == producto, presentacion].iloc[0]
        pc_raw = costos_df.loc[costos_df["Producto"] == producto, presentacion].iloc[0]
        precio_venta = float(str(pv_raw).replace(",", "").strip())
        precio_costo = float(str(pc_raw).replace(",", "").strip())
    except Exception as e:
        st.exception(e)
        die("❌ No pude obtener precio/costo para esa combinación.")

    tv, tc, sat, com, gan, res, igl, rey, pau = calcular_ganancia(
        precio_venta, precio_costo, float(cantidad), incluye_iva, pago_tarjeta
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Precio venta", precio_venta)
    c2.metric("Costo", precio_costo)
    c3.metric("Total venta", tv)
    c4.metric("Ganancia", gan)

    st.write(
        {
            "SAT": sat,
            "Comisión tarjeta": com,
            "Reserva": res,
            "Iglesia": igl,
            "Reyna": rey,
            "Paul": pau,
        }
    )


def page_inventario():
    st.header("📦 Inventario")
    if "Inventario" not in sheet_names:
        die("❌ No existe la hoja 'Inventario' en RV.xlsx")
    df = load_df(str(EXCEL_PATH), "Inventario")
    if df.empty:
        st.warning("Inventario está vacío.")
    st.dataframe(df, use_container_width=True)


def page_egresos():
    st.header("💸 Egresos")
    if "Egresos" not in sheet_names:
        die("❌ No existe la hoja 'Egresos' en RV.xlsx")
    df = load_df(str(EXCEL_PATH), "Egresos")
    if df.empty:
        st.warning("Egresos está vacío.")
    st.dataframe(df, use_container_width=True)


# ============================================================
# 7) Main UI
# ============================================================
st.title("📊 Panel de Control – ROCA VIVA / FZClean (Excel local)")

st.caption(f"📄 Fuente: {EXCEL_PATH.name} — ruta: {EXCEL_PATH}")

# Estado de arranque
dbg(f"⏱️ Tiempo total hasta UI: {_fmt_s(_now() - t_app)}")

menu = st.sidebar.radio("Navegación", ["Calculadora", "Ventas", "Inventario", "Egresos", "Diagnóstico"])

if menu == "Calculadora":
    page_calculadora()
elif menu == "Ventas":
    page_ventas()
elif menu == "Inventario":
    page_inventario()
elif menu == "Egresos":
    page_egresos()
else:
    st.header("🧰 Diagnóstico")
    st.write("Si tu app tarda en arrancar, revisa:")
    st.markdown(
        "- Que `RV.xlsx` esté en la ruta correcta.\n"
        "- Que `openpyxl` esté instalado (requirements.txt).\n"
        "- Revisa logs: errores de import, archivo no encontrado, etc."
    )
    st.write("Hojas detectadas:", sheet_names)
