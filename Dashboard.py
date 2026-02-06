import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import time

# ------------------------------
# Config UI
# ------------------------------
st.set_page_config(
    page_title="Calculadora de Ingredientes",
    page_icon="🧪",
    layout="wide",
)

# ------------------------------
# Ruta robusta al Excel
# ------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
EXCEL_PATH = SCRIPT_DIR / "RV.xlsx"
if not EXCEL_PATH.exists():
    # fallback si el archivo está en la raíz del repo
    EXCEL_PATH = Path("RV.xlsx")

# ------------------------------
# Helpers
# ------------------------------
@st.cache_resource
def get_excel_file(excel_path: str):
    # Abre estructura del Excel una sola vez
    return pd.ExcelFile(excel_path)

@st.cache_data(show_spinner=False)
def load_recetas(excel_path: str, sheet_name: str) -> pd.DataFrame:
    xl = get_excel_file(excel_path)
    df = xl.parse(sheet_name)
    if df is None or df.empty:
        return pd.DataFrame()

    # Limpieza básica
    df.columns = df.columns.astype(str).str.strip()
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # Validar columnas mínimas
    required = {"Producto", "Ingrediente", "Cantidad (L)"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Faltan columnas en '{sheet_name}': {', '.join(sorted(missing))}")

    # Expandir producto (cuando viene en blanco en filas siguientes)
    df["_Product"] = df["Producto"].replace("", np.nan).ffill()
    return df

def pretty_number(x: float) -> str:
    try:
        return f"{float(x):,.3f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return str(x)

def compute_ingredientes(df_rec: pd.DataFrame, producto: str, litros: float, base_litros: float):
    sel = df_rec[df_rec["_Product"] == producto].copy()
    sel["Cantidad (L)"] = pd.to_numeric(sel["Cantidad (L)"], errors="coerce").fillna(0.0)
    factor = litros / base_litros
    sel["Cantidad Necesaria (L)"] = sel["Cantidad (L)"] * factor
    # orden y formato
    out = sel[["Ingrediente", "Cantidad Necesaria (L)"]].copy()
    out = out.sort_values("Ingrediente")
    return out, factor

# ------------------------------
# Header (diseño)
# ------------------------------
st.markdown(
    """
    <div style="padding: 16px 18px; border-radius: 18px; border: 1px solid rgba(255,255,255,0.12);">
      <div style="display:flex; align-items:center; gap:10px;">
        <div style="font-size:32px;">🧪</div>
        <div>
          <div style="font-size:22px; font-weight:800; line-height:1.1;">Calculadora de Ingredientes</div>
          <div style="opacity:0.8; font-size:14px; margin-top:4px;">
            Lee recetas desde <b>RV.xlsx</b> y calcula cantidades para los litros que necesites.
          </div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

# ------------------------------
# Validar archivo
# ------------------------------
if not EXCEL_PATH.exists():
    st.error(
        f"❌ No encuentro **RV.xlsx**.\n\n"
        f"Busqué en:\n- {SCRIPT_DIR / 'RV.xlsx'}\n- {Path('RV.xlsx').resolve()}\n\n"
        "Súbelo al repo y colócalo en el mismo folder que `Dashboard.py` (o en la raíz)."
    )
    st.stop()

# ------------------------------
# Sidebar controls (bonito)
# ------------------------------
with st.sidebar:
    st.markdown("## ⚙️ Configuración")
    linea = st.radio("Línea", ["Roca Viva (RV)", "FZClean (FZ)"], horizontal=False)
    sheet = "Recetas RV" if "RV" in linea else "Recetas FZ"

    base_litros = st.number_input(
        "Base de receta (L)",
        min_value=1.0,
        value=200.0,
        step=10.0,
        help="Tu Excel normalmente trae recetas para 200 L. Cambia si tu base es otra.",
    )

    litros = st.number_input(
        "Litros a preparar",
        min_value=1.0,
        value=200.0,
        step=10.0,
    )

    st.divider()
    st.caption("📄 Fuente")
    st.code(str(EXCEL_PATH), language="text")

# ------------------------------
# Cargar recetas
# ------------------------------
t0 = time.perf_counter()
try:
    df_rec = load_recetas(str(EXCEL_PATH), sheet)
except Exception as e:
    st.exception(e)
    st.stop()

if df_rec.empty:
    st.warning(f"⚠️ La hoja **{sheet}** está vacía.")
    st.stop()

productos = sorted(df_rec["_Product"].dropna().unique().tolist())

# ------------------------------
# Main layout
# ------------------------------
left, right = st.columns([1.2, 1])

with left:
    st.markdown("### 🧴 Selección de producto")
    producto = st.selectbox("Producto", productos)

    # Preview de receta base (solo del producto)
    preview = df_rec[df_rec["_Product"] == producto][["Ingrediente", "Cantidad (L)"]].copy()
    preview["Cantidad (L)"] = pd.to_numeric(preview["Cantidad (L)"], errors="coerce").fillna(0.0)

    with st.expander("👀 Ver receta base (Excel)"):
        st.dataframe(preview, use_container_width=True)

    st.write("")

    c1, c2, c3 = st.columns(3)
    c1.metric("Línea", "RV" if "RV" in linea else "FZ")
    c2.metric("Base receta (L)", pretty_number(base_litros))
    c3.metric("Litros objetivo (L)", pretty_number(litros))

    st.write("")

    btn = st.button("🧮 Calcular ingredientes", use_container_width=True)

with right:
    st.markdown("### 📌 Estado")
    st.info(
        "Si no aparecen productos, revisa que tu hoja tenga columnas:\n"
        "- **Producto**\n- **Ingrediente**\n- **Cantidad (L)**\n\n"
        "Y que el nombre de hoja sea **Recetas RV** / **Recetas FZ**."
    )
    st.caption(f"⏱️ Carga inicial: {time.perf_counter() - t0:.3f}s")

# ------------------------------
# Resultado
# ------------------------------
st.write("")
st.markdown("---")

if btn:
    out, factor = compute_ingredientes(df_rec, producto, litros, base_litros)

    st.markdown("## ✅ Resultado")
    r1, r2, r3, r4 = st.columns([1, 1, 1, 1])
    r1.metric("Producto", producto)
    r2.metric("Factor", pretty_number(factor))
    r3.metric("Ingredientes", int(out.shape[0]))
    r4.metric("Hoja", sheet)

    # Formateo para mostrar bonito
    show = out.copy()
    show["Cantidad Necesaria (L)"] = show["Cantidad Necesaria (L)"].astype(float).round(3)

    st.dataframe(show, use_container_width=True, height=520)

    # Descarga CSV
    csv = show.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ Descargar resultado (CSV)",
        data=csv,
        file_name=f"ingredientes_{('RV' if 'RV' in linea else 'FZ')}_{producto}.csv".replace(" ", "_"),
        mime="text/csv",
        use_container_width=True,
    )
else:
    st.markdown(
        """
        <div style="padding: 14px 16px; border-radius: 16px; border: 1px dashed rgba(255,255,255,0.25); opacity: 0.9;">
          <b>Tip:</b> Ajusta los litros en la barra lateral y presiona <b>Calcular</b>.
        </div>
        """,
        unsafe_allow_html=True,
    )
