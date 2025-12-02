import streamlit as st
import plotly.express as px
import pandas as pd
import folium

from streamlit_folium import st_folium
from db import get_latest_data, get_sensor_locations, get_connection, get_measured_data, get_average, get_mode, get_min, get_max
from folium.features import DivIcon
from datetime import date, timedelta

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
    st.write("Selecciona una fecha o un rango de fechas directamente en el calendario:")

    # --- CALENDARIO SIEMPRE VISIBLE ---
    modo = st.radio(
        "Modo de selección:",
        ["Un solo día", "Rango de fechas"],
        horizontal=True
    )

    if modo == "Un solo día":
        fecha = st.date_input("Selecciona una fecha:", value=date.today())
        fecha_inicio = fecha
        fecha_fin = fecha
    else:
        rango = st.date_input(
            "Selecciona un rango de fechas:",
            value=(date.today() - timedelta(days=2), date.today())
        )
        if len(rango) == 1:
            fecha_inicio = rango[0]
            fecha_fin = rango[0]
        else:
            fecha_inicio = rango[0]
            fecha_fin = rango[1]

    st.markdown("---")

    # --- Obtener datos desde la DB ---
    df = get_measured_data(fecha_inicio, fecha_fin)
    if df.empty:
        st.warning("No hay registros para la fecha o rango seleccionado.")
        return

    # Ordenar por fecha y hora
    df = df.sort_values(["fecha", "hora"]).reset_index(drop=True)

    # 1. Asegurar que 'fecha' se interprete como objeto datetime.date
    #    Si la DB devuelve un Timedelta o cadena extraña, esto la limpia a un objeto de fecha/hora.
    #    Usamos errors='coerce' por si hay algún valor nulo o inválido en la DB, aunque no es ideal.
    df["fecha"] = pd.to_datetime(df["fecha"], errors='coerce').dt.normalize()
    
    # 2. Crear la columna datetime para gráficas. 
    #    Usamos .dt.strftime() para obtener una cadena de FECHA limpia ('YYYY-MM-DD').
    #    Esto evita que se añadan los indeseados '0 days' o residuos de Timedelta.
    fecha_str = df["fecha"].dt.strftime('%Y-%m-%d')
    hora_str = df["hora"].astype(str)
    
    # 3. Combina y convierte la cadena resultante a un objeto datetime final
    df["fecha_hora"] = pd.to_datetime(fecha_str + " " + hora_str)

    st.subheader("🌡️ Temperatura")
    st.line_chart(df.set_index("fecha_hora")["temp"])
    
    st.subheader("💧 Humedad")
    st.line_chart(df.set_index("fecha_hora")["humedad"])
    
    st.subheader("🧪 Gas")
    st.line_chart(df.set_index("fecha_hora")["gas"])

    st.markdown("---")

    # --- Calcular estadísticas ---
    avg = get_average(df)
    mode = get_mode(df)
    minv = get_min(df)
    maxv = get_max(df)

    st.subheader("📊 Estadísticas del periodo seleccionado")

    # --- Tarjetas en fila de 4 columnas ---
    col_prom, col_moda, col_min, col_max = st.columns(4)

    # Promedio
    with col_prom:
        st.metric("🌡️ Temp Promedio", f"{avg['temp']} °C")
        st.metric("💧 Humedad Promedio", f"{avg['humedad']} %")
        st.metric("🧪 Gas Promedio", f"{avg['gas']} ppm")

    # Moda
    with col_moda:
        st.metric("🌡️ Temp Moda", f"{mode['temp']} °C")
        st.metric("💧 Humedad Moda", f"{mode['humedad']} %")
        st.metric("🧪 Gas Moda", f"{mode['gas']} ppm")

    # Mínimo
    with col_min:
        st.metric("🌡️ Temp Mínimo", f"{minv['temp']} °C")
        st.metric("💧 Humedad Mínimo", f"{minv['humedad']} %")
        st.metric("🧪 Gas Mínimo", f"{minv['gas']} ppm")

    # Máximo
    with col_max:
        st.metric("🌡️ Temp Máximo", f"{maxv['temp']} °C")
        st.metric("💧 Humedad Máximo", f"{maxv['humedad']} %")
        st.metric("🧪 Gas Máximo", f"{maxv['gas']} ppm")


# --- SECCIÓN MODELO E-R ---
def render_modelo_er():
    st.title("Modelo E-R")
    st.write("Aquí mostraremos el diagrama Entidad-Relación.")


# --- SECCIÓN EQUIPO ---
def render_equipo():
    st.title("Equipo")
    st.write("Conoce a los miembros detrás de este proyecto y sus contribuciones")
    st.markdown("---")

    st.header("Integrantes del Proyecto")

    # --- Miembro 1: Camila ---
    st.subheader("Camila Trejo")
    col1, col2 = st.columns([1, 2]) # Columna para imagen y otra para texto
    with col1:
        # Reemplaza 'camila_foto.jpg' con la ruta real de la foto de Camila
        st.image("camila_foto.jpg", caption="Camila", width=200)
    with col2:
        st.markdown(""""
            - **Carrera:** Ingeniería en Robótica y Sistemas Digitales  
            - **Semestre:** 3er Semestre  
            - **Rol en el Proyecto:** Líder y Desarrolladora Backend
            - "..." """)
    st.markdown("---")

    # --- Miembro 2: Regina ---
    st.subheader("Regina Hernández")
    col1, col2 = st.columns([1, 2])
    with col1:
        # Reemplaza 'regina_foto.jpg' con la ruta real de la foto de Regina
        st.image("regina_foto.jpg", caption="Regina", width=200)
    with col2:
        st.markdown(f"""
            - **Carrera:** Ingeniería en Tecnologías Computacionales  
            - **Semestre:** 3er Semestre  
            - **Rol en el Proyecto:** Integración de Hardware y Análisis de Datos
            - "..." """)
    st.markdown("---")

    # --- Miembro 3: Ian ---
    st.subheader("Ian Morgado")
    col1, col2 = st.columns([1, 2])
    with col1:
        # Reemplaza 'ian_foto.jpg' con la ruta real de la foto de Ian
        st.image("ian_foto.jpg", caption="Ian", width=200)
    with col2:
        st.markdown(f"""
            - **Carrera:** Ingeniería en Tecnologías Computacionales  
            - **Semestre:** 3er Semestre  
            - **Rol en el Proyecto:** Integración de Hardware & Programador principal
            - "..." """)
    st.markdown("---")

    st.header("Momentos del Equipo")
    # --- Foto Grupal ---
    st.subheader("Equipo en acción")
    # Reemplaza 'equipo_grupal.jpg' con la ruta real de la foto grupal
    st.image("equipo_grupal.jpg", caption="El equipo trabajando en SkyMetrics", use_column_width=True)
    st.markdown("---")

    st.header("Actividades y Cronograma del Proyecto")
    # --- Imagen de Actividades ---
    st.subheader("Diagrama de Actividades")
    # Reemplaza 'actividades_proyecto.png' con la ruta real de la imagen de actividades
    st.image("actividades_proyecto.png", caption="Visión general de las actividades preliminares del proyecto", use_column_width=True)
    st.markdown("---")

