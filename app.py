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

st.title("📦 Control de Limpieza")

# --- LÓGICA DE DATOS ---
valores = hoja_inv.get_all_values()
df_inv = pd.DataFrame(valores[1:], columns=valores[0])
df_inv.columns = df_inv.columns.str.strip()
df_inv['Stock actual'] = pd.to_numeric(df_inv['Stock actual'], errors='coerce').fillna(0)
lista_productos = df_inv['Nombre del producto'].tolist()

# --- INTERFAZ ---
tab1, tab2, tab3 = st.tabs(["🛒 Registrar Venta", "➕ Nuevo Producto", "📊 Reportes"])

with tab1:
    producto = st.selectbox("Selecciona producto", lista_productos)
    cantidad = st.number_input("Litros vendidos", min_value=0.0)
    precio = st.number_input("Total Venta ($)", min_value=0.0)
    
    filtro = df_inv[df_inv['Nombre del producto'] == producto]
    if not filtro.empty:
        stock_disponible = float(filtro['Stock actual'].values[0])
        st.info(f"Stock actual de {producto}: {stock_disponible} litros")
    else:
        stock_disponible = 0
        st.warning("Producto no encontrado.")

    if st.button("Registrar Venta"):
        if cantidad > stock_disponible:
            st.error(f"⚠️ ¡Cuidado! Solo tienes {stock_disponible} litros.")
        elif cantidad <= 0:
            st.warning("La cantidad debe ser mayor a 0.")
        else:
            fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            hoja_ventas.append_row([fecha, producto, cantidad, precio, 0.0])
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
    st.subheader("📊 Reportes de Ventas")
    data_ventas = hoja_ventas.get_all_values()
    df_v = pd.DataFrame(data_ventas[1:], columns=data_ventas[0])
    df_v.columns = df_v.columns.str.strip()
    
    # --- CORRECCIÓN AQUÍ: Usamos los nombres exactos de tu hoja ---
    df_v['Fecha'] = pd.to_datetime(df_v['Fecha'], dayfirst=True)
    df_v['Cantidad_Litros'] = pd.to_numeric(df_v['Cantidad_Litros']) 
    df_v['Total Venta'] = pd.to_numeric(df_v['Total Venta'])
    
    hoy = datetime.now()
    inicio_semana = hoy - pd.Timedelta(days=hoy.weekday())
    df_semanal = df_v[df_v['Fecha'] >= inicio_semana]
    
    col1, col2 = st.columns(2)
    col1.metric("Litros semanales", f"{df_semanal['Cantidad_Litros'].sum():,.2f} L")
    col2.metric("Ventas semanales ($)", f"${df_semanal['Total Venta'].sum():,.2f}")
    
    st.write("---")
    st.write("Desglose por producto:")
    resumen = df_semanal.groupby('Producto').agg({'Cantidad_Litros': 'sum', 'Total Venta': 'sum'}).reset_index()
    st.table(resumen)
