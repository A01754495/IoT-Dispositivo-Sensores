import streamlit as st
import plotly.express as px
import pandas as pd
import folium

from streamlit_folium import st_folium
from db import get_latest_data, get_sensor_locations
from folium.features import DivIcon

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

    sensors = get_sensor_locations()
    if not sensors: 
        st.warning("No hay ubicaciones")
        return 
    
    # Centrar mapa en la primera posición
    first = sensors[0]
    m = folium.Map(location=[first["lat"], first["lon"]], zoom_start=13)

    # LISTA de coordenadas para dibujar la ruta
    route = []

    for s in sensors:
        route.append([s["lat"], s["lon"]])

        folium.Marker(
            [s["lat"], s["lon"]],
            popup=f"""
                <b>Sensor:</b> {s['id_sensor']}<br>
                <b>Lat:</b> {s['lat']}<br>
                <b>Lon:</b> {s['lon']}<br>
            """,
            icon=DivIcon(
                icon_size=(40,40),
                icon_anchor=(20,20),
                html=f'''
                <div style="
                    background-color:#003333;
                    width:40px;
                    height:40px;
                    border-radius:50%;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    font-size:22px;
                    color:white;
                    box-shadow:0px 0px 8px #1F6FEBAA;
                    border:2px solid white;
                ">
                    📡
                </div>
                '''
            )
        ).add_to(m)

    # DIBUJAR RUTA EN EL MAPA
    folium.PolyLine(
        route,
        color="purple",
        weight=4,
        opacity=0.8
    ).add_to(m)

    st_folium(m, width=900, height=500)


# --- SECCIÓN DESCRIPCIÓN ---
def render_inicio():
    st.title("Descripción")
    st.write("Página de bienvenida del sistema.")


# --- SECCIÓN CALENDARIO ---
def render_calendario():
    st.title("Calendario")
    st.write("Aquí pondremos la selección de fechas y filtros.")

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
