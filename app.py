import streamlit as st
import gspread
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE CONEXIÓN ---
creds_dict = st.secrets["gcp_service_account"]
gc = gspread.service_account_from_dict(creds_dict)
sh = gc.open('App-Limpieza-Inventario')
hoja_inv = sh.worksheet('Inventario')
hoja_ventas = sh.worksheet('Ventas')
hoja_reportes = sh.worksheet('Reportes')

st.title("📦 Control de Limpieza")

# --- LÓGICA DE DATOS ---
# Leemos datos de inventario para validaciones
valores = hoja_inv.get_all_values()
df_inv = pd.DataFrame(valores[1:], columns=valores[0])
df_inv.columns = df_inv.columns.str.strip()
# Convertimos stock a numérico para poder comparar
df_inv['Stock actual'] = pd.to_numeric(df_inv['Stock actual'])
lista_productos = df_inv['Nombre del producto'].tolist()

# --- INTERFAZ ---
tab1, tab2, tab3 = st.tabs(["🛒 Registrar Venta", "➕ Nuevo Producto", "📊 Reportes"])

with tab1:
    producto = st.selectbox("Selecciona producto", lista_productos)
    cantidad = st.number_input("Litros vendidos", min_value=0.0)
    precio = st.number_input("Total Venta ($)", min_value=0.0)
    
    # Mostrar stock actual como referencia
    stock_disponible = df_inv.loc[df_inv['Nombre del producto'] == producto, 'Stock actual'].values[0]
    st.info(f"Stock actual de {producto}: {stock_disponible} litros")

    if st.button("Registrar Venta"):
        # --- VALIDACIÓN ---
        if cantidad > stock_disponible:
            st.error(f"⚠️ ¡Cuidado! Solo tienes {stock_disponible} litros. No puedes vender {cantidad}.")
        elif cantidad <= 0:
            st.warning("La cantidad debe ser mayor a 0.")
        else:
            fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
            # Registramos venta
            hoja_ventas.append_row([fecha, producto, cantidad, precio, 0.0])
            
            # Actualizamos stock
            celda = hoja_inv.find(producto)
            hoja_inv.update_cell(celda.row, 3, stock_disponible - cantidad)
            
            st.success(f"¡Venta de {producto} registrada!")
            st.rerun()

with tab2:
    st.subheader("Agregar nuevo producto")
    nuevo_nom = st.text_input("Nombre del producto")
    capacidad = st.number_input("Capacidad maxima", min_value=0.0)
    stock_ini = st.number_input("Existencia inicial")
    precio_v = st.number_input("Precio venta", min_value=0.0)
    costo_u = st.number_input("Costo unidad", min_value=0.0)
    
    if st.button("Guardar Producto"):
        hoja_inv.append_row([nuevo_nom, capacidad, stock_ini, precio_v, costo_u])
        st.success("Producto guardado correctamente")
        st.rerun()

with tab3:
    st.subheader("Resumen de Reportes")
    # Leemos la hoja reportes y la mostramos
    data_rep = hoja_reportes.get_all_values()
    df_rep = pd.DataFrame(data_rep[1:], columns=data_rep[0])
    st.dataframe(df_rep)
