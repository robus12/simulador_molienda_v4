import streamlit as st
import pandas as pd
import random
import time
import matplotlib.pyplot as plt

# Configuración inicial
TODOS_LOS_SILOS = {
    'Maíz Nacional': {'stock': 50.0, 'tasa': 0.5},
    'Maíz Importado': {'stock': 50.0, 'tasa': 0.4},
    'Trigo': {'stock': 50.0, 'tasa': 0.3},
    'Soya': {'stock': 50.0, 'tasa': 0.6}
}

if "silos" not in st.session_state:
    st.session_state.silos = TODOS_LOS_SILOS.copy()

if "molino" not in st.session_state:
    st.session_state.molino = {'capacidad': 10.0, 'estado_actual': 0.0, 'tasa_molienda': 1.0}

if "total_molido" not in st.session_state:
    st.session_state.total_molido = 0.0

if "historial" not in st.session_state:
    st.session_state.historial = []

if "productos_dia" not in st.session_state:
    st.session_state.productos_dia = []

if "imagen_generada" not in st.session_state:
    st.session_state.imagen_generada = False

# Título
st.title("Simulador de Molienda - Jornada de 8 Horas (Toneladas)")

# Selección de productos
if not st.session_state.productos_dia:
    seleccion = st.multiselect(
        "Selecciona 1 o 2 productos que se molerán hoy:",
        list(TODOS_LOS_SILOS.keys())
    )
    if len(seleccion) > 2:
        st.error("Solo puedes seleccionar 1 o 2 productos.")
    elif seleccion:
        st.session_state.productos_dia = seleccion
        st.success(f"Seleccionados: {', '.join(seleccion)}")
    st.stop()

productos_validos = st.session_state.productos_dia
TOTAL_PASOS = 120
CAPACIDAD_TOTAL_MOLINO = TOTAL_PASOS * st.session_state.molino['tasa_molienda']

# Simular 10 pasos
if st.button("Simular 10 pasos manuales"):
    for _ in range(10):
        silos_validos = [k for k in productos_validos
                         if st.session_state.silos[k]['stock'] > 0 and st.session_state.molino['estado_actual'] < st.session_state.molino['capacidad']]

        if silos_validos:
            silo = random.choice(silos_validos)
            descarga = min(
                st.session_state.silos[silo]['tasa'],
                st.session_state.silos[silo]['stock'],
                st.session_state.molino['capacidad'] - st.session_state.molino['estado_actual']
            )
            st.session_state.silos[silo]['stock'] -= descarga
            st.session_state.molino['estado_actual'] += descarga

            molienda = min(st.session_state.molino['estado_actual'], st.session_state.molino['tasa_molienda'])
            st.session_state.molino['estado_actual'] -= molienda
            st.session_state.total_molido += molienda

            st.session_state.historial.append({
                'Paso': len(st.session_state.historial) + 1,
                'Silo': silo,
                'Molido (ton)': molienda
            })
        time.sleep(0.05)

# Simular jornada completa
if st.button("Simular Jornada Completa (120 pasos)"):
    for _ in range(TOTAL_PASOS):
        silos_validos = [k for k in productos_validos
                         if st.session_state.silos[k]['stock'] > 0 and st.session_state.molino['estado_actual'] < st.session_state.molino['capacidad']]

        if silos_validos:
            silo = random.choice(silos_validos)
            descarga = min(
                st.session_state.silos[silo]['tasa'],
                st.session_state.silos[silo]['stock'],
                st.session_state.molino['capacidad'] - st.session_state.molino['estado_actual']
            )
            st.session_state.silos[silo]['stock'] -= descarga
            st.session_state.molino['estado_actual'] += descarga

            molienda = min(st.session_state.molino['estado_actual'], st.session_state.molino['tasa_molienda'])
            st.session_state.molino['estado_actual'] -= molienda
            st.session_state.total_molido += molienda

            st.session_state.historial.append({
                'Paso': len(st.session_state.historial) + 1,
                'Silo': silo,
                'Molido (ton)': molienda
            })
        time.sleep(0.05)
    st.success("Jornada completada.")

# Visualización
st.subheader("Estado del Molino")
st.progress(st.session_state.molino['estado_actual'] / st.session_state.molino['capacidad'])

col1, col2 = st.columns(2)
col1.metric("Molino actual", f"{st.session_state.molino['estado_actual']:.2f} ton")
col2.metric("Total molido", f"{st.session_state.total_molido:.2f} ton")

# Gráfico de stock
st.subheader("Stock actual de silos")
df_stock = pd.DataFrame({k: v['stock'] for k, v in st.session_state.silos.items()}, index=["Stock"]).T
st.bar_chart(df_stock)

# Historial y resumen
if st.session_state.historial:
    df_hist = pd.DataFrame(st.session_state.historial)
    resumen = df_hist.groupby("Silo").agg({
        "Molido (ton)": "sum",
        "Paso": "count"
    }).rename(columns={"Molido (ton)": "Total Molido (ton)", "Paso": "Veces Usado"})

    eficiencia = (st.session_state.total_molido / CAPACIDAD_TOTAL_MOLINO) * 100

    st.subheader("Historial del proceso")
    st.line_chart(df_hist.set_index("Paso")[["Molido (ton)"]])
    st.dataframe(df_hist)

    st.subheader("Resumen final por producto")
    st.dataframe(resumen)
    st.metric("Eficiencia del molino", f"{eficiencia:.2f} %")

    # Generar imagen visual tipo infografía
    if not st.session_state.imagen_generada:
        fig, ax = plt.subplots(figsize=(10, 6))
        df_hist.groupby("Paso")["Molido (ton)"].sum().plot(ax=ax, color='green', linewidth=2)
        ax.set_title("Línea de Tiempo del Proceso de Molienda", fontsize=14)
        ax.set_xlabel("Paso (simulado)", fontsize=10)
        ax.set_ylabel("Toneladas molidas", fontsize=10)
        ax.grid(True)
        plt.tight_layout()
        plt.savefig("reporte_molienda.png")
        st.session_state.imagen_generada = True

    st.image("reporte_molienda.png", caption="Reporte Visual de la Jornada", use_column_width=True)

# Reiniciar
if st.button("Reiniciar Jornada"):
    st.session_state.clear()
    st.experimental_rerun()