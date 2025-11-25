// WiFi y contraseña de IoT del Tec
#define IOT_CONFIG_WIFI_SSID "Tec-IoT"
#define IOT_CONFIG_WIFI_PASSWORD "spotless.magnetic.bridge"

// Azure IoT Hub
#define IOT_CONFIG_IOTHUB_FQDN "CIRhub.azure-devices.net"
// Azure IoT Hub Device ID
#define IOT_CONFIG_DEVICE_ID "ESP32_test"
// Azure IoT Hub Device Key (primary key)
#define IOT_CONFIG_DEVICE_KEY "7fRBl7VWoWFS/hIS7d7KEfiruDu8zoMqzScZbpversE="

// Manda un mensaje cada 2 segundos
#define TELEMETRY_FREQUENCY_MILLISECS 2000

// Dirección MAC, que usaremos
// como identificador único
#define MAC "ec:e3:34:21:a2:e0"

// Dirección IP del dispositivo donde
// la base de datos se almacenará
#define IP_SERVERDB "10.48.68.11"

// Localización en latitud y longitud del ESP32
//#define LOCATION 1 // CEDETEC
//#define LOCATION 2 // Biblio
//#define LOCATION  // Gimnasio Pofesional
//#define LOCATION  // Aulas 3
//#define LOCATION  // Estadio Borregos