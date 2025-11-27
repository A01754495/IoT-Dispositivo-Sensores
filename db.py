import mysql.connector
from datetime import date, time
from pandas import DataFrame, Series

# --- CONEXION SQL ---
def get_connection():
    return mysql.connector.connect(
        host="localhost", 
        user="esp32",
        password="ESP32-IoT-equipo1",
        database="Reto"
    )


# --- DATOS SQL ---
def get_latest_data():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            (SELECT medida_temp FROM Registro_temp ORDER BY fecha DESC, hora DESC LIMIT 1) AS temp,
            (SELECT medida_humedad FROM Registro_humedad ORDER BY fecha DESC, hora DESC LIMIT 1) AS humedad,
            (SELECT medida_gas FROM Registro_gas ORDER BY fecha DESC, hora DESC LIMIT 1) AS gas
    """)

    data = cursor.fetchone()
    conn.close()
    return data


# --- OBTENER LUGAR ---
def get_sensor_locations():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT id_sensor, lugar 
        FROM sensor
    """)

    rows = cursor.fetchall()
    conn.close()

    sensors = []
    for r in rows: 
        try: 
            lat_str, lon_str = r["lugar"].split(",")
            sensors.append({
                "id_sensor": r["id_sensor"],
                "lat": float(lat_str.strip()),
                "lon": float(lon_str.strip())  
            })
        except:
            print(f"ERROR en lugar: {r['lugar']}")

    return sensors

# --- OBTENER VALORES MEDIDOS EN RANGO DE FECHAS ---
def get_measured_data(fromDate, toDate): # El formato de fecha debe estar así: "YYYY-MM-DD"
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    fromDate = fromDate.split("-")
    fromDate = date(int(fromDate[0]), int(fromDate[1]), int(fromDate[2]))

    toDate = toDate.split("-")
    toDate = date(int(toDate[0]), int(toDate[1]), int(toDate[2]))

    query = ("""
        SELECT Registro_temp.fecha, Registro_temp.hora, medida_temp AS temp, medida_humedad AS humedad, medida_gas AS gas FROM Registro_temp
            INNER JOIN Registro_humedad on Registro_humedad.fecha = Registro_temp.fecha AND Registro_humedad.hora = Registro_temp.hora
            INNER JOIN Registro_gas on Registro_temp.fecha = Registro_gas.fecha AND Registro_temp.hora = Registro_gas.hora
            WHERE Registro_temp.fecha BETWEEN %s AND %s
            ORDER BY Registro_temp.fecha DESC, Registro_temp.hora DESC;
    """)
    try:
        cursor.execute(query, (fromDate, toDate))
    except:
        print(f"ERROR en el rango de fechas!")

    rows = cursor.fetchall()
    conn.close()

    return DataFrame(rows) # Regresa un objeto DataFrame con los registros obtenidos

# --- OBTENER PROMEDIOS DEL DATAFRAME ---
def get_average(data): # Es preferible así porque get_measured_data es una función que toma mucho tiempo
    return data.mean(numeric_only=True).round(2)

# --- OBTENER MODAS DEL DATAFRAME ---
def get_mode(data): # Es preferible así porque get_measured_data es una función que toma mucho tiempo
    return data.mode(numeric_only=True).head(1)

# --- OBTENER MÁXIMOS DEL DATAFRAME ---
def get_max(data): # Es preferible así porque get_measured_data es una función que toma mucho tiempo
    return data.max(numeric_only=True)

# --- OBTENER MÍNIMOS DEL DATAFRAME ---
def get_min(data): # Es preferible así porque get_measured_data es una función que toma mucho tiempo
    return data.min(numeric_only=True)