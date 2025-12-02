import mysql.connector
from datetime import date, time, datetime
from pandas import DataFrame
from collections import defaultdict

# --- CONEXION SQL ---
def get_connection():
    return mysql.connector.connect(
        host="localhost", 
        user="root",
        password="",
        database="reto2"
    )


# --- DATOS SQL ---
def get_latest_data():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            (SELECT medida_temp FROM registro_temp ORDER BY fecha DESC, hora DESC LIMIT 1) AS temp,
            (SELECT medida_humedad FROM registro_humedad ORDER BY fecha DESC, hora DESC LIMIT 1) AS humedad,
            (SELECT medida_gas FROM registro_gas ORDER BY fecha DESC, hora DESC LIMIT 1) AS gas
    """)

    data = cursor.fetchone()
    conn.close()
    return data


# --- OBTENER LUGAR ---
def get_sensor_locations():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT idSensor, coordenadas AS coord, descripcion AS "desc" FROM sensor
            INNER JOIN lugar ON sensor.idLugar = lugar.idLugar; 
    """)

    rows = cursor.fetchall()
    conn.close()

    sensors_list = []

    for row in rows:
        # La columna 'coordenadas' tiene el formato "latitud, longitud" (ej: "19.597..., -99.277...")
        # Debemos separar esta cadena en dos números flotantes
        try:
            # Asegúrate de que las coordenadas se separen por coma y espacio, o solo coma
            lat_str, lon_str = row['coord'].split(',')
            lat = float(lat_str.strip()) # strip() elimina espacios innecesarios
            lon = float(lon_str.strip())
            
            sensors_list.append({
                "id_sensor": row['idSensor'],
                "lat": lat,
                "lon": lon,
                "desc": row['desc']
            })
        except Exception as e:
            # Manejo de error si el formato de coordenadas es incorrecto
            print(f"Error al procesar coordenadas para Sensor {row.get('idSensor', 'N/A')}: {row['coordenadas']} -> {e}")
            continue

    # Regresa una lista simple de diccionarios, mucho más fácil de iterar
    return sensors_list

# --- OBTENER MEDICIONES EN RANGO DE FECHAS ---
def get_measured_data(fromDate, toDate):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    #fromDate = fromDate.split("-")
    #fromDate = date(int(fromDate[0]), int(fromDate[1]), int(fromDate[2]))

    #toDate = toDate.split("-")
    #toDate = date(int(toDate[0]), int(toDate[1]), int(toDate[2]))

    query = ("""
        SELECT registro_temp.fecha, registro_temp.hora, medida_temp AS temp, medida_humedad AS humedad, medida_gas AS gas FROM registro_temp
            INNER JOIN registro_humedad on registro_humedad.fecha = registro_temp.fecha AND registro_humedad.hora = registro_temp.hora
            INNER JOIN registro_gas on registro_temp.fecha = registro_gas.fecha AND registro_temp.hora = registro_gas.hora
            WHERE registro_temp.fecha BETWEEN %s AND %s
            ORDER BY registro_temp.fecha ASC, registro_temp.hora ASC;
    """)
    try:
        cursor.execute(query, (fromDate, toDate))
    except:
        print(f"ERROR en el rango de fechas!")

    rows = cursor.fetchall()
    conn.close()

    return DataFrame(rows) # Regresa un objeto DataFrame con los registros obtenidos

# --- OBTENER MEDICIONES EN RANGO DE FECHAS ---
# --- HACE CAST A LAS FECHAS Y HORAS A DATETIME ---
def get_measured_data_castdatetime(fromDate, toDate):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    fromDate = fromDate.strftime("%Y-%m-%d")
    toDate = toDate.strftime("%Y-%m-%d")

    query = ("""
        SELECT STR_TO_DATE(CONCAT(registro_temp.fecha, ' ', registro_temp.hora), '%Y-%m-%d %H:%i:%s') AS fechaHora,
            medida_temp AS temp, medida_humedad AS humedad, medida_gas AS gas FROM registro_temp
            INNER JOIN registro_humedad on registro_humedad.fecha = registro_temp.fecha AND registro_humedad.hora = registro_temp.hora
            INNER JOIN registro_gas on registro_temp.fecha = registro_gas.fecha AND registro_temp.hora = registro_gas.hora
            WHERE registro_temp.fecha BETWEEN '{0}' AND '{1}'
            ORDER BY registro_temp.fecha ASC, registro_temp.hora ASC;
    """).format(fromDate, toDate)

    try:
        cursor.execute(query)
    except:
        print(f"ERROR en el rango de fechas!")

    rows = cursor.fetchall()
    conn.close()

    return DataFrame(rows) # Regresa un objeto DataFrame con los registros obtenidos 

# --- FUNCIONES WRAPPER ---

# --- OBTENER PROMEDIOS DEL DATAFRAME ---
def get_average(data): # Es preferible así porque get_measured_data es una función que toma mucho tiempo
    return data.mean(numeric_only=True).round(2)

# --- OBTENER MODAS DEL DATAFRAME ---
def get_mode(data): # Es preferible así porque get_measured_data es una función que toma mucho tiempo
    return data.mode(numeric_only=True).loc[0]

# --- OBTENER MÁXIMOS DEL DATAFRAME ---
def get_max(data): # Es preferible así porque get_measured_data es una función que toma mucho tiempo
    return data.max(numeric_only=True)

# --- OBTENER MÍNIMOS DEL DATAFRAME ---
def get_min(data): # Es preferible así porque get_measured_data es una función que toma mucho tiempo
    return data.min(numeric_only=True)