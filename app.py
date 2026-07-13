import streamlit as st
import gspread
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE CONEXIÓN ---
# Se conecta a través de los "Secrets" que configuramos en la nube
# Asegúrate de haber guardado el bloque TOML corregido anteriormente en Streamlit Cloud
creds_dict = st.secrets["gcp_service_account"]
gc = gspread.service_account_from_dict(creds_dict)
sh = gc.open('App-Limpieza-Inventario')
hoja_inv = sh.worksheet('Inventario')
hoja_ventas = sh.worksheet('Ventas')

st.title("📦 Control de Limpieza")

# --- LÓGICA DE DATOS ---
# Obtenemos todos los datos para extraer la lista de productos correctamente
# Esto evita el KeyError al no depender de una columna inexistente antes de cargar
valores = hoja_inv.get_all_values()
df_inv = pd.DataFrame(valores[1:], columns=valores[0])

# Ahora lista_productos se extrae de la columna 'Nombre del producto'
# (Verifica que en tu hoja 'Inventario' la columna se llame así exactamente)
df_inv.columns = df_inv.columns.str.strip()
lista_productos = df_inv['Nombre del producto'].tolist()
# --- INTERFAZ ---
tab1, tab2 = st.tabs(["🛒 Registrar Venta", "➕ Nuevo Producto"])

with tab1:
    producto = st.selectbox("Selecciona producto", lista_productos)
    cantidad = st.number_input("Litros vendidos", min_value=0.0)
    precio = st.number_input("Total Venta ($)", min_value=0.0)
    # Calculamos ganancia estimada (si tienes costo unitario en la columna 5)
    ganancia = 0.0 # Ajusta esta lógica según necesites

    if st.button("Registrar Venta"):
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
        # Registramos en Ventas: Fecha, Producto, Cantidad, Precio, Ganancia
        hoja_ventas.append_row([fecha, producto, cantidad, precio, ganancia])
        
        # Actualizamos stock en hoja Inventario
        # Buscamos la fila basándonos en el nombre del producto
        celda = hoja_inv.find(producto)
        stock_actual = float(hoja_inv.cell(celda.row, 3).value)
        hoja_inv.update_cell(celda.row, 3, stock_actual - cantidad)
        
        st.success(f"¡Venta de {producto} registrada!")
        st.rerun() # Actualiza la app para reflejar el nuevo stock

with tab2:
    st.subheader("Agregar nuevo producto")
    nuevo_nom = st.text_input("Nombre del producto")
    capacidad = st.number_input("Capacidad maxima", min_value=0.0)
    stock_ini = st.number_input("Existencia inicial")
    precio_v = st.number_input("Precio venta", min_value=0.0)
    costo_u = st.number_input("Costo unidad", min_value=0.0)
    
    if st.button("Guardar Producto"):
        # Ajustado a tus 5 columnas: Nombre, Capacidad, Stock, Precio, Costo
        hoja_inv.append_row([nuevo_nom, capacidad, stock_ini, precio_v, costo_u])
        st.success("Producto guardado correctamente")
        st.rerun()
