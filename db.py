import mysql.connector
from datetime import date
from pandas import DataFrame
from collections import defaultdict

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
        SELECT idSensor, coordenadas AS coord, descripcion AS "desc" FROM Sensor
            INNER JOIN Lugar on Sensor.idLugar = Lugar.idLugar; 
    """)

    rows = cursor.fetchall()
    conn.close()

    sensors = defaultdict(list)
    for row in rows:
        if 'idSensor' in row and 'coord' in row and 'desc' in row:
            sensors[row['idSensor']].append({
                "coord": row['coord'], 
                "desc": row['desc']
            })
        else:
            print(f"ERROR en la recuperación del lugar!")

    # Regresa un diccionario con las llaves del idSensor, ligadas a una lista de
    # diccionarios con llaves coord y desc

    # Ejemplo de cómo recuperar los datos: get_sensor_locations()[0][0]['coord'];
    # [0] es la llave idSensor, [0] es el índice al de la lista, ['coord'] es la llave de las coordenadas
    return dict(sensors)

# --- OBTENER MEDICIONES EN RANGO DE FECHAS ---
def get_measured_data(fromDate, toDate): # El formato de fecha debe ser: YYYY-MM-DD
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