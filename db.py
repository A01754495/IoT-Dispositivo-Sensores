import mysql.connector
from datetime import date, time
from pandas import DataFrame, Series

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

# --- OBTENER VALORES MEDIDOS ---
def get_measured_data(fromDate, toDate): # el formato de fecha debe estar así: "YYYY-MM-DD"
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    fromDate = fromDate.split("-")
    fromDate = date(int(fromDate[0]), int(fromDate[1]), int(fromDate[2]))

    toDate = toDate.split("-")
    toDate = date(int(toDate[0]), int(toDate[1]), int(toDate[2]))

    query = ("""
        SELECT registro_temp.fecha, registro_temp.hora, medida_temp, medida_humedad, medida_gas FROM registro_temp
            INNER JOIN registro_humedad on registro_humedad.fecha = registro_temp.fecha AND registro_humedad.hora = registro_temp.hora
            INNER JOIN registro_gas on registro_temp.fecha = registro_gas.fecha AND registro_temp.hora = registro_gas.hora
            WHERE registro_temp.fecha BETWEEN %s AND %s
            ORDER BY registro_temp.fecha DESC, registro_temp.hora DESC;
    """)
    try:
        cursor.execute(query, (fromDate, toDate))
    except:
        print(f"ERROR en el rango de fechas!")

    rows = cursor.fetchall()
    conn.close()

    data = DataFrame(rows)

    return data



data = get_measured_data("2025-11-25","2025-11-25")
print(data)