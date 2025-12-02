import streamlit as st
import time 
import pandas as pd
import mysql.connector
import pathlib
import matplotlib.pyplot as plt
import folium

from streamlit_folium import st_folium
from db import get_latest_data
from secciones import nav_button, render_skymetrics, render_inicio, render_calendario, render_inicio, render_calendario, render_modelo_er, render_equipo
from datetime import date, timedelta

# --- DISEÑO DE LA PESTAÑA ---
st.set_page_config(
    page_title="SkyMetrics",
    page_icon="📡",
    layout="wide"
)


# --- CSS ---
current_dir = pathlib.Path(__file__).parent
css_file = current_dir / "style.css"

with open("style.css", "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# --- CARGAR DATOS SQL ---
latest_data = get_latest_data()

temp = latest_data["temp"]
hum = latest_data["humedad"]
gas = latest_data["gas"]


# --- SIDEBAR ---
st.sidebar.title("Navegación")


# --- INICIALIZAR PÁGINA ---
if "page" not in st.session_state:
    st.session_state.page = "Equipo"


# --- BOTONES DEL MENÚ ---
nav_button("SkyMetrics")
nav_button("Descripción")
nav_button("Calendario")
nav_button("Modelo E-R")
nav_button("Equipo")

page = st.session_state.page


# --- RENDER DE CADA SECCIÓN ---
if page == "SkyMetrics": 
    render_skymetrics()

elif page == "Descripción":
    render_inicio()

elif page == "Calendario":
    render_calendario()

elif page == "Modelo E-R":
    render_modelo_er()

elif page == "Equipo":
    render_equipo()
