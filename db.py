import mysql.connector


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
