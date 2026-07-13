import streamlit as st
import gspread
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE CONEXIÓN ---
# Se conecta usando los secretos configurados en Streamlit Cloud
creds_dict = st.secrets["gcp_service_account"]
gc = gspread.service_account_from_dict(creds_dict)
sh = gc.open('App-Limpieza-Inventario')
hoja_inv = sh.worksheet('Inventario')
hoja_ventas = sh.worksheet('Ventas')

st.set_page_config(page_title="Control de Limpieza", layout="centered")
st.title("📦 Control de Limpieza")

# --- LÓGICA DE DATOS ---
# Obtenemos productos desde la columna A de la hoja 'Inventario'
datos_inv = hoja_inv.get_all_records()
df_inv = pd.DataFrame(datos_inv)
lista_productos = df_inv['Producto'].tolist()

# --- INTERFAZ ---
tab1, tab2, tab3 = st.tabs(["🛒 Registrar Venta", "📊 Stock Actual", "➕ Nuevo Producto"])

with tab1:
    st.subheader("Registrar Venta")
    producto = st.selectbox("Selecciona producto", lista_productos)
    cantidad = st.number_input("Cantidad (Litros/Kilos)", min_value=0.0, step=0.5)
    precio = st.number_input("Total Venta ($)", min_value=0.0)

    if st.button("Registrar Venta"):
        try:
            # 1. Registrar en hoja Ventas
            fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            hoja_ventas.append_row([fecha, producto, cantidad, precio])
            
            # 2. Actualizar stock en hoja Inventario
            # Buscamos la fila del producto
            fila_idx = df_inv[df_inv['Producto'] == producto].index[0] + 2
            stock_actual = float(hoja_inv.cell(fila_idx, 3).value)
            
            nuevo_stock = stock_actual - cantidad
            hoja_inv.update_cell(fila_idx, 3, nuevo_stock)
            
            st.success(f"✅ Venta registrada: {producto} ({cantidad} unidades). Quedan {nuevo_stock} en stock.")
        except Exception as e:
            st.error(f"Error al registrar: {e}")

with tab2:
    st.subheader("Inventario en existencia")
    # Mostramos el stock actualizado
    datos_actualizados = hoja_inv.get_all_records()
    st.dataframe(pd.DataFrame(datos_actualizados))

with tab3:
    st.subheader("Alta de nuevo producto")
    nuevo_nom = st.text_input("Nombre del producto (ej: Cloro 5L)")
    stock_ini = st.number_input("Existencia inicial", min_value=0.0)
    
    if st.button("Guardar Producto"):
        if nuevo_nom:
            hoja_inv.append_row([nuevo_nom, "General", stock_ini])
            st.success(f"Producto '{nuevo_nom}' guardado. Refresca la app para verlo en ventas.")
        else:
            st.warning("Escribe un nombre de producto.")
