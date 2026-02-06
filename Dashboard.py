import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

# ------------------------------
# UI Config (mobile-first)
# ------------------------------
st.set_page_config(page_title="Calculadora RV/FZ", page_icon="🧪", layout="centered")

# ------------------------------
# Excel path
# ------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
EXCEL_PATH = SCRIPT_DIR / "RV.xlsx"
if not EXCEL_PATH.exists():
    EXCEL_PATH = Path("RV.xlsx")

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

    df.columns = df.columns.astype(str).str.strip()
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    required = {"Producto", "Ingrediente", "Cantidad (L)"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Faltan columnas: {', '.join(sorted(missing))}")

    df["_Product"] = df["Producto"].replace("", np.nan).ffill()
    df["Cantidad (L)"] = pd.to_numeric(df["Cantidad (L)"], errors="coerce").fillna(0.0)

    return df

def format_qty(l):
    l = float(l)
    if l < 1:
        ml = l * 1000
        return f"{int(round(ml))} mL" if abs(ml-round(ml)) < 1e-6 else f"{ml:.1f} mL"
    else:
        s = f"{l:.3f}".rstrip("0").rstrip(".")
        return f"{s} L"

def ingredient_cards(df):
    for _, r in df.iterrows():
        st.markdown(
            f"""
            <div style="
              border:1px solid rgba(255,255,255,.15);
              border-radius:14px;
              padding:10px 12px;
              margin-bottom:8px;
              background:rgba(255,255,255,.03);
            ">
              <div style="font-size:15px;font-weight:700;">{r['Ingrediente']}</div>
              <div style="font-size:18px;font-weight:900;margin-top:4px;">
                {format_qty(r['Cantidad Necesaria (L)'])}
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )

# ------------------------------
# Header
# ------------------------------
st.markdown(
    """
    <div style="padding:10px 12px;border-radius:16px;border:1px solid rgba(255,255,255,.12)">
      <div style="font-size:20px;font-weight:900;">🧪 Calculadora de Ingredientes</div>
      <div style="font-size:12px;opacity:.8">Cambia litros y se actualiza al momento</div>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("")

if not EXCEL_PATH.exists():
    st.error("❌ No se encontró RV.xlsx")
    st.stop()

# ------------------------------
# Controles compactos
# ------------------------------
c1, c2 = st.columns(2)

with c1:
    linea = st.segmented_control("Línea", ["RV", "FZ"], default="RV")

with c2:
    litros = st.number_input(
        "Litros",
        min_value=0.1,
        value=200.0,
        step=0.1,
        format="%.1f"
    )

sheet = "Recetas RV" if linea == "RV" else "Recetas FZ"

df_rec = load_recetas(str(EXCEL_PATH), sheet)

productos = sorted(df_rec["_Product"].dropna().unique())
producto = st.selectbox("Producto", productos)

# ------------------------------
# Calcular instantáneo
# ------------------------------
base_litros = 200.0
factor = litros / base_litros

sel = df_rec[df_rec["_Product"] == producto].copy()
sel["Cantidad Necesaria (L)"] = sel["Cantidad (L)"] * factor

out = sel[["Ingrediente", "Cantidad Necesaria (L)"]].sort_values("Ingrediente")

# ------------------------------
# Mini resumen en una sola línea
# ------------------------------
st.markdown(
    f"""
    <div style="font-size:12px;opacity:.75;margin:6px 0 10px 0;">
      Línea: <b>{linea}</b> &nbsp;|&nbsp;
      Litros: <b>{format_qty(litros)}</b> &nbsp;|&nbsp;
      Ingredientes: <b>{len(out)}</b>
    </div>
    """,
    unsafe_allow_html=True
)

# ------------------------------
# Tarjetas (rápido de ver)
# ------------------------------
ingredient_cards(out)

# ------------------------------
# Descarga opcional
# ------------------------------
csv = out.assign(
    Cantidad_texto=out["Cantidad Necesaria (L)"].apply(format_qty)
).to_csv(index=False).encode("utf-8-sig")

st.download_button(
    "⬇️ Descargar CSV",
    csv,
    file_name=f"ingredientes_{linea}_{producto}.csv".replace(" ", "_"),
    use_container_width=True
)
