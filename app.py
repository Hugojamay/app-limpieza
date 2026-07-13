import streamlit as st
import gspread
from datetime import datetime

# 1. Configuración de conexión (necesitarás subir el archivo llave.json a GitHub)
gc = gspread.service_account(filename='llave.json')
sh = gc.open('App-Limpieza-Inventario')
hoja_inv = sh.worksheet('Inventario')
hoja_ventas = sh.worksheet('Ventas')

st.title("📦 Control de Limpieza")

# 2. Formulario para celular
producto = st.selectbox("Selecciona producto", hoja_inv.col_values(1)[1:])
cantidad = st.number_input("Litros vendidos", min_value=0.0)
precio = st.number_input("Total Venta", min_value=0.0)
ganancia = st.number_input("Ganancia", min_value=0.0)

if st.button("Registrar Venta"):
    # Registro y resta de inventario
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    hoja_ventas.append_row([fecha, producto, cantidad, precio, ganancia])
    
    cell = hoja_inv.find(producto)
    stock_actual = float(hoja_inv.cell(cell.row, 3).value)
    hoja_inv.update_cell(cell.row, 3, stock_actual - cantidad)
    
    st.success(f"¡Venta de {producto} registrada!")