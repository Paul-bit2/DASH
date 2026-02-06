import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# 0) Archivo Excel local (en el repo de GitHub)
# ============================================================
EXCEL_PATH = Path(__file__).with_name("RV.xlsx")


# ============================================================
# 1) Helpers de lectura
# ============================================================
def _assert_excel_exists():
    if not EXCEL_PATH.exists():
        st.error(
            f"❌ No se encontró el archivo **{EXCEL_PATH.name}**\n\n"
            "👉 Debe estar en el mismo folder que app.py (subido a GitHub)"
        )
        st.stop()


def list_worksheets():
    _assert_excel_exists()
    try:
        xl = pd.ExcelFile(EXCEL_PATH)
        return xl.sheet_names
    except Exception as e:
        st.error(f"❌ No pude abrir el Excel: {e}")
        st.stop()


@st.cache_data(show_spinner=False)
def load_df(ws_name: str) -> pd.DataFrame:
    _assert_excel_exists()
    try:
        df = pd.read_excel(EXCEL_PATH, sheet_name=ws_name)
    except ValueError:
        st.error(
            f"❌ No existe la hoja '{ws_name}'.\n\n"
            "Hojas disponibles:\n  • " + "\n  • ".join(list_worksheets())
        )
        st.stop()
    except Exception as e:
        st.error(f"❌ Error leyendo '{ws_name}': {e}")
        st.stop()

    if df is None or df.empty:
        st.error(f"❌ La hoja '{ws_name}' está vacía.")
        st.stop()

    # Limpieza básica
    df.columns = df.columns.astype(str).str.strip()
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    return df


# ============================================================
# 2) Cálculo de ganancias (solo para mostrar)
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
# 3) Páginas
# ============================================================
def page_calculadora():
    st.header("🧪 Calculadora de Ingredientes")

    linea = st.selectbox("Línea de productos", ["Roca Viva (RV)", "FZClean (FZ)"])
    ws_recetas = "Recetas RV" if "RV" in linea else "Recetas FZ"

    df_rec = load_df(ws_recetas)

    if "Producto" not in df_rec.columns:
        st.error("❌ La hoja debe tener columna 'Producto'")
        st.stop()

    if "Ingrediente" not in df_rec.columns or "Cantidad (L)" not in df_rec.columns:
        st.error("❌ Faltan columnas 'Ingrediente' o 'Cantidad (L)'")
        st.stop()

    # Expandir productos
    df_rec["_Product"] = df_rec["Producto"].replace("", np.nan).ffill()
    productos = sorted(df_rec["_Product"].dropna().unique().tolist())

    producto = st.selectbox("Producto", productos)

    litros = st.number_input(
        "Litros a preparar",
        min_value=1.0,
        step=1.0,
        value=200.0
    )

    if st.button("Calcular ingredientes"):
        sel = df_rec[df_rec["_Product"] == producto].copy()

        base_litros = 200.0
        factor = litros / base_litros

        sel["Cantidad (L)"] = pd.to_numeric(sel["Cantidad (L)"], errors="coerce").fillna(0)
        sel["Cantidad Necesaria (L)"] = sel["Cantidad (L)"] * factor

        st.dataframe(
            sel[["Ingrediente", "Cantidad Necesaria (L)"]],
            use_container_width=True
        )


def page_ventas():
    st.header("💰 Simulador de Venta (solo lectura)")

    precios_df = load_df("Precio Venta")
    costos_df = load_df("Costos")

    if "Producto" not in precios_df.columns or "Producto" not in costos_df.columns:
        st.error("❌ Ambas hojas deben tener columna 'Producto'")
        st.stop()

    productos = sorted(precios_df["Producto"].dropna().unique().tolist())
    producto = st.selectbox("Producto", productos)

    pres = [c for c in precios_df.columns if c != "Producto" and c in costos_df.columns]

    if not pres:
        st.error("❌ No hay presentaciones coincidentes entre Precio y Costos")
        st.stop()

    presentacion = st.selectbox("Presentación", pres)

    cantidad = st.number_input("Cantidad", min_value=1.0, step=1.0, value=1.0)
    incluye_iva = st.checkbox("¿Precio incluye IVA?", value=True)
    pago_tarjeta = st.checkbox("¿Pago con tarjeta?", value=False)

    try:
        pv = precios_df.loc[precios_df["Producto"] == producto, presentacion].iloc[0]
        pc = costos_df.loc[costos_df["Producto"] == producto, presentacion].iloc[0]

        precio_venta = float(str(pv).replace(",", ""))
        precio_costo = float(str(pc).replace(",", ""))

    except Exception as e:
        st.error(f"❌ Error obteniendo valores: {e}")
        st.stop()

    st.markdown(f"**Precio venta:** {precio_venta}")
    st.markdown(f"**Costo:** {precio_costo}")

    tv, tc, sat, com, gan, res, igl, rey, pau = calcular_ganancia(
        precio_venta,
        precio_costo,
        cantidad,
        incluye_iva,
        pago_tarjeta
    )

    st.subheader("📊 Resultado")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total venta", tv)
    col2.metric("Total costo", tc)
    col3.metric("Ganancia", gan)

    st.write(
        {
            "SAT": sat,
            "Comisión tarjeta": com,
            "Reserva": res,
            "Iglesia": igl,
            "Reyna": rey,
            "Paul": pau
        }
    )


def page_inventario():
    st.header("📦 Inventario")
    st.dataframe(load_df("Inventario"), use_container_width=True)


def page_egresos():
    st.header("💸 Egresos")
    st.dataframe(load_df("Egresos"), use_container_width=True)


# ============================================================
# 4) Menú principal
# ============================================================
def main():
    st.title("📊 Panel – ROCA VIVA / FZClean (Excel local)")

    st.sidebar.caption(f"📄 Fuente: {EXCEL_PATH.name}")

    menu = st.sidebar.radio(
        "Navegación",
        ["Calculadora", "Ventas", "Inventario", "Egresos"]
    )

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
