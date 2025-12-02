import streamlit as st
import plotly.express as px
import pandas as pd
import folium

from streamlit_folium import st_folium
from db import get_latest_data, get_sensor_locations, get_connection, get_measured_data, get_average, get_mode, get_min, get_max, get_measured_data_castdatetime
from folium.features import DivIcon
from folium.plugins import MarkerCluster
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

    st.markdown("### Gráficas de PowerBI")
    st.markdown("---")

    st.markdown("### Mapa de sensores")

    sensors = get_sensor_locations()
    if not sensors:
        st.warning("No hay ubicaciones registradas.")
        return

    # Centrar mapa en el primer sensor
    first = sensors[0]
    m = folium.Map(
        location=[first["lat"], first["lon"]],
        zoom_start=16,
        tiles="cartodbpositron"
    )

    route = []

    for s in sensors:
        route.append([s["lat"], s["lon"]])

        icon_html = """
        <div style='
            background-color:#58A6FF;
            width:38px; height:38px;
            border-radius:50%;
            display:flex; 
            align-items:center; 
            justify-content:center;
            font-size:22px; 
            color:white;
            border:2px solid white;
            box-shadow:0 0 6px #58A6FFAA;
        '>📡</div>
        """

        folium.Marker(
            location=[s["lat"], s["lon"]],
            popup=f"<b>Sensor:</b> {s['id_sensor']}<br><b>Lugar:</b> {s['desc']}",
            icon=DivIcon(html=icon_html, icon_size=(40,40), icon_anchor=(20,20))
        ).add_to(m)

    if len(route) > 1:
        folium.PolyLine(
            route, color="#58A6FF", weight=3, opacity=0.8
        ).add_to(m)

    st_folium(m, width=900, height=500)



# --- SECCIÓN DESCRIPCIÓN ---
def render_inicio():
    st.title("Descripción del proyecto")
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
    col1, col2 = st.columns([1, 2])
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

    # Para la selección de un solo día o rango de día
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

    # Usar la función que devuelve el DATETIME ya unido
    df = get_measured_data_castdatetime(fecha_inicio, fecha_fin) 
    
    if df.empty:
        st.warning("No hay registros para la fecha o rango seleccionado.")
        return

    # Calular estadísticas
    avg = get_average(df)
    mode = get_mode(df)
    minv = get_min(df)
    maxv = get_max(df)

    st.subheader("Estadísticas")

    # Leyenda para los colores e identificar temperatura, humedad y gas 
    legend_html = f"""
    <div style="font-size: 14px; margin-top: -10px; margin-bottom: 20px;">
        <span class='legend-box metric-temp'></span> Temperatura
        <span class='legend-box metric-humedad'></span> Humedad
        <span class='legend-box metric-gas'></span> Gas
    </div>
    """
    st.markdown(legend_html, unsafe_allow_html=True)

    st.markdown("#### Promedio")
    # Definir 3 Columnas: Temperatura, Humedad, Gas
    col_temp, col_humedad, col_gas = st.columns(3)
    # Asignamos la métrica a cada columna
    with col_temp:
    # Usamos la clase CSS 'metric-temp'
        st.markdown(f'<div class="metric-container metric-temp"><div class="metric-value">{avg["temp"]:.2f} °C</div></div>', unsafe_allow_html=True)
    with col_humedad:
        # Usamos la clase CSS 'metric-humedad'
        st.markdown(f'<div class="metric-container metric-humedad"><div class="metric-value">{avg["humedad"]:.2f} %</div></div>', unsafe_allow_html=True)
    with col_gas:
        # Usamos la clase CSS 'metric-gas'
        st.markdown(f'<div class="metric-container metric-gas"><div class="metric-value">{avg["gas"]:.2f} ppm</div></div>', unsafe_allow_html=True)
        

    st.markdown("#### Moda")
    col_temp, col_humedad, col_gas = st.columns(3) 

    with col_temp:
        st.markdown(f'<div class="metric-container metric-temp"><div class="metric-value">{mode["temp"]} °C</div></div>', unsafe_allow_html=True)
    with col_humedad:
        st.markdown(f'<div class="metric-container metric-humedad"><div class="metric-value">{mode["humedad"]} %</div></div>', unsafe_allow_html=True)
    with col_gas:
        st.markdown(f'<div class="metric-container metric-gas"><div class="metric-value">{mode["gas"]} ppm</div></div>', unsafe_allow_html=True)
        

    st.markdown("#### Mínimo")
    col_temp, col_humedad, col_gas = st.columns(3) 

    with col_temp:
        st.markdown(f'<div class="metric-container metric-temp"><div class="metric-value">{minv["temp"]:.2f} °C</div></div>', unsafe_allow_html=True)
    with col_humedad:
        st.markdown(f'<div class="metric-container metric-humedad"><div class="metric-value">{minv["humedad"]:.2f} %</div></div>', unsafe_allow_html=True)
    with col_gas:
        st.markdown(f'<div class="metric-container metric-gas"><div class="metric-value">{minv["gas"]:.2f} ppm</div></div>', unsafe_allow_html=True)


    st.markdown("#### Máximo")
    col_temp, col_humedad, col_gas = st.columns(3) 

    with col_temp:
        st.markdown(f'<div class="metric-container metric-temp"><div class="metric-value">{maxv["temp"]:.2f} °C</div></div>', unsafe_allow_html=True)
    with col_humedad:
        st.markdown(f'<div class="metric-container metric-humedad"><div class="metric-value">{maxv["humedad"]:.2f} %</div></div>', unsafe_allow_html=True)
    with col_gas:
        st.markdown(f'<div class="metric-container metric-gas"><div class="metric-value">{maxv["gas"]:.2f} ppm</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    # La columna ya viene limpia y combinada como fechaHora.
    # Establecemos como índice fechaHora para los gráficos.
    df_plot = df.set_index("fechaHora")
    st.subheader("Gráficas")

    col_temp, col_humedad, col_gas = st.columns(3) 
    with col_temp: 
        st.markdown("#### Temperatura")
        st.line_chart(df.set_index("fechaHora")["temp"])
    
    with col_humedad:
        st.markdown("#### Humedad")
        st.line_chart(df.set_index("fechaHora")["humedad"])
    
    with col_gas:
        st.markdown("#### Gas")
        st.line_chart(df.set_index("fechaHora")["gas"])


    
# --- SECCIÓN MODELO E-R ---
def render_modelo_er():
    st.title("Modelo E-R")
    st.write("Aquí mostraremos el diagrama Entidad-Relación.")


# --- SECCIÓN EQUIPO ---
def render_equipo():
    st.title("Equipo")
    st.write("Conoce a los miembros detrás de este proyecto y sus contribuciones")
    col_cam, col_regi, col_ia = st.columns(3) 

    with col_cam: 
        st.subheader("Camila Trejo")
        
        # Contenedor para CENTRAR todos los elementos
        st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
        
        # Muestra la imagen (se centra dentro del <div>)
        st.image("camila_.jpg", caption=None, width=200)

        # Muestra el texto formateado (el caption)
        # Usamos HTML para los saltos de línea
        caption_html = f"""
        <div style="font-size: 14px; margin-top: 5px;">
            <b>Carrera:</b> IRS <br>
            <b>Semestre:</b> 3er Semestre <br>
            <b>Rol:</b> Líder y Desarrolladora Frontend <br> 
            <b>"A Sky Full of Stars - Coldplay"</b>
        </div>
        """
        st.markdown(caption_html, unsafe_allow_html=True)
        
        # Cierre del contenedor de centrado
        st.markdown('</div>', unsafe_allow_html=True)

    with col_regi:
        st.subheader("Regina Hernández")
        st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
        # st.image("regi_.jpg", caption=None, width=200)

        caption_html = f"""
        <div style="font-size: 14px; margin-top: 5px;">
            <b>Carrera:</b> ITC <br>
            <b>Semestre:</b> 3er Semestre <br>
            <b>Rol:</b> Encargada de electrónica <br> 
            <b>"..."</b>
        </div>
        """
        st.markdown(caption_html, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_ia:
        st.subheader("Ian Morgado")
        st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
        st.image("ian_.jpg", caption=None, width=300)

        caption_html = f"""
        <div style="font-size: 14px; margin-top: 5px;">
            <b>Carrera:</b> ITC <br>
            <b>Semestre:</b> 3er Semestre <br>
            <b>Rol:</b> Encargada de electrónica <br> 
            <b>"..."</b>
        </div>
        """
        st.markdown(caption_html, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    st.header("Actividades y Cronograma del Proyecto")
    # Quitar comentario cuando tengamos la imagen
    # st.image("actividades_proyecto.png", caption="Visión general de las actividades preliminares del proyecto", use_column_width=True)

    # Agregar texto en viñetas para las actividades que se realizan (las que hizo pupa regi en el doc de control y seguimiento) 

