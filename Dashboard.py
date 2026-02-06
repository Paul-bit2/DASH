import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

# ------------------------------
# UI Config (mobile-friendly)
# ------------------------------
st.set_page_config(page_title="Calculadora RV/FZ", page_icon="🧪", layout="centered")

# ------------------------------
# Excel path (robusto)
# ------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
EXCEL_PATH = SCRIPT_DIR / "RV.xlsx"
if not EXCEL_PATH.exists():
    EXCEL_PATH = Path("RV.xlsx")  # fallback raíz repo

# ------------------------------
# Helpers
# ------------------------------
@st.cache_resource
def get_excel(excel_path: str):
    return pd.ExcelFile(excel_path)

@st.cache_data(show_spinner=False)
def load_recetas(excel_path: str, sheet_name: str) -> pd.DataFrame:
    xl = get_excel(excel_path)
    df = xl.parse(sheet_name)
    if df is None or df.empty:
        return pd.DataFrame()

    df.columns = df.columns.astype(str).str.strip()
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    required = {"Producto", "Ingrediente", "Cantidad (L)"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Faltan columnas en '{sheet_name}': {', '.join(sorted(missing))}")

    df["_Product"] = df["Producto"].replace("", np.nan).ffill()
    df["Cantidad (L)"] = pd.to_numeric(df["Cantidad (L)"], errors="coerce").fillna(0.0)
    return df

def format_qty_l_or_ml(liters_value: float) -> str:
    """
    Regla:
      - >= 1.0  -> mostrar en L
      - <  1.0  -> mostrar en mL (ej .9 -> 900 mL)
    """
    v = float(liters_value)

    if v < 1.0:
        ml = v * 1000.0
        # si es casi entero, sin decimales
        if abs(ml - round(ml)) < 1e-9:
            return f"{int(round(ml)):,} mL".replace(",", " ")
        # si no, 1 decimal
        return f"{ml:,.1f} mL".replace(",", " ").replace(".0", "")
    else:
        # litros: 3 decimales si hace falta, pero sin ceros inútiles
        s = f"{v:,.3f} L".replace(",", " ")
        s = s.replace("0 L", " L")
        # quitar ceros al final tipo 2.500 -> 2.5
        s = s.replace(" L", "")
        if "." in s:
            s = s.rstrip("0").rstrip(".")
        return s + " L"

def ingredient_cards(df_out: pd.DataFrame):
    # Tarjetas simples usando markdown (se ven bien en celular)
    for _, r in df_out.iterrows():
        ing = str(r["Ingrediente"])
        qty = float(r["Cantidad Necesaria (L)"])
        pretty = format_qty_l_or_ml(qty)

        st.markdown(
            f"""
            <div style="
              border: 1px solid rgba(255,255,255,0.14);
              border-radius: 16px;
              padding: 12px 14px;
              margin-bottom: 10px;
              background: rgba(255,255,255,0.03);
            ">
              <div style="font-weight:800; font-size:16px; line-height:1.2;">{ing}</div>
              <div style="margin-top:6px; font-size:20px; font-weight:900;">{pretty}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

# ------------------------------
# Start
# ------------------------------
st.markdown(
    """
    <div style="padding: 12px 14px; border-radius: 18px; border: 1px solid rgba(255,255,255,0.12);">
      <div style="display:flex; gap:10px; align-items:center;">
        <div style="font-size:30px;">🧪</div>
        <div>
          <div style="font-size:20px; font-weight:900;">Calculadora de Ingredientes</div>
          <div style="opacity:0.85; font-size:13px;">Cambia litros y se actualiza al momento.</div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.write("")

if not EXCEL_PATH.exists():
    st.error(
        "❌ No encuentro RV.xlsx.\n\n"
        "Súbelo al repo y colócalo:\n"
        "- en el mismo folder que Dashboard.py, o\n"
        "- en la raíz del repo."
    )
    st.stop()

# ------------------------------
# Selector "todo en el mismo espacio"
# ------------------------------
# En celular, columns se apilan; en desktop quedan en fila.
c1, c2 = st.columns([1, 1])

with c1:
    linea = st.segmented_control(
        "Línea",
        options=["RV", "FZ"],
        default="RV",
    )

with c2:
    litros = st.number_input(
        "Litros a preparar",
        min_value=0.1,
        step=0.1,
        value=200.0,
        format="%.1f",
        help="Ej: 200.0"
    )

sheet = "Recetas RV" if linea == "RV" else "Recetas FZ"

try:
    df_rec = load_recetas(str(EXCEL_PATH), sheet)
except Exception as e:
    st.exception(e)
    st.stop()

if df_rec.empty:
    st.warning(f"⚠️ La hoja '{sheet}' está vacía.")
    st.stop()

productos = sorted(df_rec["_Product"].dropna().unique().tolist())

producto = st.selectbox("Producto", productos)

# ------------------------------
# Cálculo instantáneo
# ------------------------------
base_litros = 200.0  # tu estándar
factor = float(litros) / float(base_litros)

sel = df_rec[df_rec["_Product"] == producto].copy()
sel["Cantidad Necesaria (L)"] = sel["Cantidad (L)"] * factor
out = sel[["Ingrediente", "Cantidad Necesaria (L)"]].copy()
out = out.sort_values("Ingrediente")

# ------------------------------
# Resumen + salida bonita
# ------------------------------
st.markdown("### ✅ Resultado")
k1, k2, k3 = st.columns(3)
k1.metric("Línea", linea)
k2.metric("Litros", format_qty_l_or_ml(float(litros)))
k3.metric("Ingredientes", int(out.shape[0]))

# Tarjetas por ingrediente (mobile-first)
ingredient_cards(out)

# Opcional: descarga rápida
csv = out.assign(
    **{"Cantidad (texto)": out["Cantidad Necesaria (L)"].apply(format_qty_l_or_ml)}
).to_csv(index=False).encode("utf-8-sig")

st.download_button(
    "⬇️ Descargar (CSV)",
    data=csv,
    file_name=f"ingredientes_{linea}_{producto}.csv".replace(" ", "_"),
    mime="text/csv",
    use_container_width=True,
)
