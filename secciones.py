import streamlit as st
import plotly.express as px
import pandas as pd
import folium

from streamlit_folium import st_folium
from db import get_latest_data, get_sensor_locations
from folium.features import DivIcon
from datetime import datetime, timedelta, date

# --- NAVEGACIÓN BOTONES ---
def nav_button(name):
    active = st.session_state.page == name
    if st.sidebar.button(f"{name}", key=name):
        st.session_state.page = name


# --- SECCIÓN SKYMETRICS ---
def render_skymetrics():
    st.title("📡 SkyMetrics")
    st.write("Bienvenido al panel principal")

    ## Gráficas de ejemplo (luego conectamos SQL por fechas)
    st.markdown("### 📈 Gráficas de sensores")
    st.markdown("---")

    ## Mapa
    st.markdown("### 🌍 Mapa de sensores")

    # sensors = get_sensor_locations()
    # if not sensors: 
    #     st.warning("No hay ubicaciones")
    #     return 
    
    # # Centrar mapa en la primera posición
    # first = sensors[0]
    # m = folium.Map(location=[first["lat"], first["lon"]], zoom_start=13)

    # # LISTA de coordenadas para dibujar la ruta
    # route = []

    # for s in sensors:
    #     route.append([s["lat"], s["lon"]])

    #     folium.Marker(
    #         [s["lat"], s["lon"]],
    #         popup=f"""
    #             <b>Sensor:</b> {s['id_sensor']}<br>
    #             <b>Lat:</b> {s['lat']}<br>
    #             <b>Lon:</b> {s['lon']}<br>
    #         """,
    #         icon=DivIcon(
    #             icon_size=(40,40),
    #             icon_anchor=(20,20),
    #             html=f'''
    #             <div style="
    #                 background-color:#003333;
    #                 width:40px;
    #                 height:40px;
    #                 border-radius:50%;
    #                 display:flex;
    #                 align-items:center;
    #                 justify-content:center;
    #                 font-size:22px;
    #                 color:white;
    #                 box-shadow:0px 0px 8px #1F6FEBAA;
    #                 border:2px solid white;
    #             ">
    #                 📡
    #             </div>
    #             '''
    #         )
    #     ).add_to(m)

    # # DIBUJAR RUTA EN EL MAPA
    # folium.PolyLine(
    #     route,
    #     color="purple",
    #     weight=4,
    #     opacity=0.8
    # ).add_to(m)

    # st_folium(m, width=900, height=500)


# --- SECCIÓN DESCRIPCIÓN ---
def render_inicio():
    st.title("Descripción del proyecto")

    # --- DESCRIPCIÓN ---#
    st.subheader("**¿En qué consiste?**")
    col1, col2 = st.columns([2, 1]) # izquieda más grande que la derecha 
    with col1: 
        st.markdown(""" Este proyecto consiste en diseñar e implementar un sistema para la adquisición, procesamiento y
                visualización de datos amientales en tiempo real, utilizando una estación de monitoreo basadas 
                en el microcontrolador ESP32. La estación estará equipada como 2 sensores capaces de registrar 
                la temperatura, humedad y concentración de gases. La información recolectada será enviada mediante 
                conexión WiFi a una base de datos MySQL, encargada de almacenar y organizar los datos generados.""")
        st.markdown("""Además, se desarrolló una interfaz de usuario que permita visualizar los registros de manera clara
                e intuitiva, optimizando la comprensión y el acceso a la información desde computadoras y dispositivos móviles.""")
        st.subheader("**Necesidad**")
        st.markdown(""" Este proyecto consiste en diseñar e implementar un sistema para la adquisición, procesamiento y
                visualización de datos amientales en tiempo real, utilizando una estación de monitoreo basadas 
                en el microcontrolador ESP32. La estación estará equipada como 2 sensores capaces de registrar 
                la temperatura, humedad y concentración de gases. La información recolectada será enviada mediante 
                conexión WiFi a una base de datos MySQL, encargada de almacenar y organizar los datos generados.""")
    with col2: 
        st.image("estacion.jpg", caption = "Estación meteorológica Equipo 1", width=350)

    
    st.subheader("**Beneficios**")
    st.markdown("""- Adquirir comprensión integral del proceso que implica el diseño y la implementación de una base de datos funcional.
- Reforzar las habilidades en programación, gestión de datos, conexión de hardware, análisis de información en tiempo real, 
trabajo en equipo y organización de proyectos
- Entendimiento profundo sobre el uso de tecnologías de diversas áreas, trabajando en conjunto para crear aplicaciones funcionales
- Fomentar la conciencia sobre la importancia de la calidad de aire y el impacto del entorno en la vida cotidiana""")
    
    st.subheader("**Recursos Materiales**")
    st.markdown("""- Computadoras con sistema operativo de uso general como Windows, MacOS o Linux
- ESP32
- Sensores DHT11 (humedad y temperatura) y MQ2 (gases)
- Componentes electrónicos (jumpers, cables, protoboard y pila)
- Contenedor acrílico para resguardar la estación meteorológica """)
    col1, col2 = st.columns([1, 2]) # izquieda más grande que la derecha 
    with col1: 
        st.subheader("**Recursos Digitales**")
        st.markdown("""- Software Arduino, junto con sus bibliotecas y controladores para el ESP32 y los sensores
- Software XAMPP
- Implementación del lenguaje de programación Python y algún editor/IDE que soporte notebooks Jupyter
- Licencias de estudiante de Microsoft Power BI
- Software de administración de proyectos como GanttProject
- Accesibilidad a servidores de base de datos
- Servicio de procesamiento de eventos (Azure Event Hubs)""")
        
    with col2: 
        st.image("rec_digitales.png", width=900)
    
    st.subheader("**Tabla de Inversión**")
    costos = {
        "Componente": ["Kit de electrónica", "ESP32", "Batería recargable", "Contenedor de acrílico"],
        "Costo $MXN (IVA incluido)": [954, 184, 159, 200]
    }

    df_costos = pd.DataFrame(costos) #organización de datos en filas y columnas 
    st.dataframe(df_costos, hide_index=True, width=600) #tabla interactiva y no muestra los índices

    st.markdown("""**Total de inversión aproximada:** $1,865 MXN (IVA incluido)""")


# --- SECCIÓN CALENDARIO ---
def render_calendario():
    st.title("Calendario")
    st.write("Selecciona una fecha o un rango de fechas directamente en el calendario:")

    # --- CALENDARIO SIEMPRE VISIBLE ---
    fecha = st.date_input(
        "Calendario",
        value=[datetime.date.today()],
        min_value=datetime.date(2024, 1, 1),
        max_value=datetime.date.today(),
        format="YYYY-MM-DD"
    )

    st.markdown("---")

    # -------------------------------
    #      INTERPRETAR SELECCIÓN
    # -------------------------------
    if isinstance(fecha, list) and len(fecha) == 2:
        # RANGO DE FECHAS
        fecha_inicio, fecha_fin = fecha
        st.subheader(f"📆 Registros del {fecha_inicio} al {fecha_fin}")

        modo = "rango"

    elif isinstance(fecha, list) and len(fecha) == 1:
        # SOLO UN DÍA
        fecha = fecha[0]
        st.subheader(f"📆 Registros del {fecha}")

        modo = "dia"

    else:
        st.warning("Selecciona una fecha válida.")
        return

    # -------------------------------------
    #   AQUÍ VA LA CONSULTA SQL REAL
    # -------------------------------------
    # Por ahora te meto datos de ejemplo:
    registros = pd.DataFrame({
        "hora": ["08:00", "09:30", "11:15", "14:20", "17:10"],
        "temperatura": [22, 23, 24, 26, 21],
        "humedad": [60, 58, 55, 52, 59],
        "gas": [200, 180, 195, 210, 205]
    }).sort_values("hora")

    # -------------------------------------
    #       MOSTRAR REGISTROS
    # -------------------------------------
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🌡️ Temperatura")
        for _, r in registros.iterrows():
            st.markdown(
                f"<div style='padding:10px;background:#1f2937;border-radius:10px;margin-bottom:6px;'>"
                f"<strong>{r['hora']}</strong> — {r['temperatura']} °C</div>",
                unsafe_allow_html=True
            )

    with col2:
        st.markdown("### 💧 Humedad")
        for _, r in registros.iterrows():
            st.markdown(
                f"<div style='padding:10px;background:#113a5f;border-radius:10px;margin-bottom:6px;'>"
                f"<strong>{r['hora']}</strong> — {r['humedad']} %</div>",
                unsafe_allow_html=True
            )

    with col3:
        st.markdown("### 🧪 Gas")
        for _, r in registros.iterrows():
            st.markdown(
                f"<div style='padding:10px;background:#3f1e5f;border-radius:10px;margin-bottom:6px;'>"
                f"<strong>{r['hora']}</strong> — {r['gas']} ppm</div>",
                unsafe_allow_html=True
            )

    st.markdown("---")

    st.markdown("### Promedio")
    ## Datos reales
    data = get_latest_data()

    temperatura = data["temp"]
    humedad = data["humedad"]
    gas = data["gas"]

    ## Tarjetas
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🌡️ Temperatura", f"{temperatura} °C")

    with col2:
        st.metric("💧 Humedad", f"{humedad} %")

    with col3:
        st.metric("🧪 Gas", f"{gas} ppm")

    st.markdown("---")
    
    st.markdown("### Moda")
    ## Datos reales
    data = get_latest_data()

    temperatura = data["temp"]
    humedad = data["humedad"]
    gas = data["gas"]

    ## Tarjetas
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🌡️ Temperatura", f"{temperatura} °C")

    with col2:
        st.metric("💧 Humedad", f"{humedad} %")

    with col3:
        st.metric("🧪 Gas", f"{gas} ppm")

    st.markdown("---")
    
    st.markdown("### Mínimo")
    ## Datos reales
    data = get_latest_data()

    temperatura = data["temp"]
    humedad = data["humedad"]
    gas = data["gas"]

    ## Tarjetas
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🌡️ Temperatura", f"{temperatura} °C")

    with col2:
        st.metric("💧 Humedad", f"{humedad} %")

    with col3:
        st.metric("🧪 Gas", f"{gas} ppm")

    st.markdown("---")
    
    st.markdown("### Máximo")
    ## Datos reales
    data = get_latest_data()

    temperatura = data["temp"]
    humedad = data["humedad"]
    gas = data["gas"]

    ## Tarjetas
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🌡️ Temperatura", f"{temperatura} °C")

    with col2:
        st.metric("💧 Humedad", f"{humedad} %")

    with col3:
        st.metric("🧪 Gas", f"{gas} ppm")

    st.markdown("---")


# --- SECCIÓN MODELO E-R ---
def render_modelo_er():
    st.title("Modelo E-R")
    st.write("Aquí mostraremos el diagrama entidad-relación.")


# --- SECCIÓN EQUIPO ---
def render_equipo():
    st.title("Equipo")
    st.write("Camila — Regina — Ian")
