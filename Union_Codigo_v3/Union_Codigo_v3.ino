// Azure IoT SDK for C includes
#include <az_core.h>
#include <az_iot.h>
#include <azure_ca.h>

// Libraries for MQTT client, WiFi connection,
// NTP Client, Date computation and HTTP Client
#include <Arduino_JSON.h>
#include <HTTPClient.h>
#include <mqtt_client.h>
#include <NTPClient.h>
#include <TimeLib.h>
#include <WebServer.h>
#include <WiFi.h>
#include <WiFiUdp.h>
// Additional sample headers
#include "AzIoTSasToken.h"
#include "SerialLogger.h"
#include "iot_configs.h"

#include "DHT.h"

#define MQ2PIN 34
#define DHTPIN 4
#define DHTTYPE DHT11
#define idDHT1 0
#define idDHT2 1
#define idMQ2 2

// When developing for your own Arduino-based platform,
// please follow the format '(ard;<platform>)'.
#define AZURE_SDK_CLIENT_USER_AGENT "c%2F" AZ_SDK_VERSION_STRING "(ard;esp32)"

// Utility macros and defines
#define sizeofarray(a) (sizeof(a) / sizeof(a[0]))
#define NTP_SERVERS "pool.ntp.org", "time.nist.gov"
#define MQTT_QOS1 1
#define DO_NOT_RETAIN_MSG 0
#define SAS_TOKEN_DURATION_IN_MINUTES 60
#define UNIX_TIME_NOV_13_2017 1510592825

#define PST_TIME_ZONE -6
#define PST_TIME_ZONE_DAYLIGHT_SAVINGS_DIFF 0

// Tiempo de desfase con respecto a GMT +00:00
// GMT -06:00 = -3600 * 6 = -21600
#define GMT_OFFSET_SECS (PST_TIME_ZONE * 3600)
#define GMT_OFFSET_SECS_DST ((PST_TIME_ZONE + PST_TIME_ZONE_DAYLIGHT_SAVINGS_DIFF) * 3600)

DHT dht(DHTPIN, DHTTYPE);
WebServer server(80);
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP);

// Variables globales para calcular
// la Fecha y Hora formateadas
static time_t t = 0UL;
static String dayStamp = "";
static String timeStamp = "";

// Variables globales para guardar
// la Humedad, la Temperatura y el Gas
static float humedad = 0.0f;
static float temperatura = 0.0f;
static float gas = 0.0f;

String telemetry_payload = "";

// Conexión a servidor con base de datos
static const String servidorDB = "http://" + String(IP_SERVERDB) + "/IoT/insertaDatos.php";
//static const String servidorDB = "http://10.48.68.11/IoT/insertaDatos.php";

// Localización en latitud y longitud del ESP32
static const String ubicacion = String(LOCATION);

// Translate iot_configs.h defines into variables used by the sample
static const char* ssid = IOT_CONFIG_WIFI_SSID;
static const char* password = IOT_CONFIG_WIFI_PASSWORD;
static const char* host = IOT_CONFIG_IOTHUB_FQDN;
static const char* mqtt_broker_uri = "mqtts://" IOT_CONFIG_IOTHUB_FQDN;
static const char* device_id = IOT_CONFIG_DEVICE_ID;
static const int mqtt_port = AZ_IOT_DEFAULT_MQTT_CONNECT_PORT;
static const String mac = String(MAC);

// Memory allocated for the sample's variables and structures.
static esp_mqtt_client_handle_t mqtt_client;
static az_iot_hub_client client;

static char mqtt_client_id[128];
static char mqtt_username[128];
static char mqtt_password[200];
static uint8_t sas_signature_buffer[256];
static unsigned long next_telemetry_send_time_ms = 0;
static char telemetry_topic[128];
static uint32_t telemetry_send_count = 0;

#define INCOMING_DATA_BUFFER_SIZE 128
static char incoming_data[INCOMING_DATA_BUFFER_SIZE];

// Auxiliary functions
#ifndef IOT_CONFIG_USE_X509_CERT
static AzIoTSasToken sasToken(
  &client,
  AZ_SPAN_FROM_STR(IOT_CONFIG_DEVICE_KEY),
  AZ_SPAN_FROM_BUFFER(sas_signature_buffer),
  AZ_SPAN_FROM_BUFFER(mqtt_password));
#endif  // IOT_CONFIG_USE_X509_CERT

static void connectToWiFi() {
  Logger.Info("Connecting to WIFI SSID " + String(ssid));

  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(100);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");

  Logger.Info("WiFi connected, IP address: " + WiFi.localIP().toString());
}

static void initializeTime() {
  Logger.Info("Setting time using SNTP");

  configTime(GMT_OFFSET_SECS, GMT_OFFSET_SECS_DST, NTP_SERVERS);
  time_t now = time(NULL);
  while (now < UNIX_TIME_NOV_13_2017) {
    delay(500);
    Serial.print(".");
    now = time(nullptr);
  }
  Serial.println("");
  Logger.Info("Time initialized!");
}

void receivedCallback(char* topic, byte* payload, unsigned int length) {
  Logger.Info("Received [");
  Logger.Info(topic);
  Logger.Info("]: ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println("");
}

#if defined(ESP_ARDUINO_VERSION_MAJOR) && ESP_ARDUINO_VERSION_MAJOR >= 3
static void mqtt_event_handler(void* handler_args, esp_event_base_t base, int32_t event_id, void* event_data) {
  (void)handler_args;
  (void)base;
  (void)event_id;

  esp_mqtt_event_handle_t event = (esp_mqtt_event_handle_t)event_data;
#else   // ESP_ARDUINO_VERSION_MAJOR
static esp_err_t mqtt_event_handler(esp_mqtt_event_handle_t event) {
#endif  // ESP_ARDUINO_VERSION_MAJOR
  switch (event->event_id) {
    int i, r;

    case MQTT_EVENT_ERROR:
      Logger.Info("MQTT event MQTT_EVENT_ERROR");
      break;
    case MQTT_EVENT_CONNECTED:
      Logger.Info("MQTT event MQTT_EVENT_CONNECTED");

      r = esp_mqtt_client_subscribe(mqtt_client, AZ_IOT_HUB_CLIENT_C2D_SUBSCRIBE_TOPIC, 1);
      if (r == -1) {
        Logger.Error("Could not subscribe for cloud-to-device messages.");
      } else {
        Logger.Info("Subscribed for cloud-to-device messages; message id:" + String(r));
      }

      break;
    case MQTT_EVENT_DISCONNECTED:
      Logger.Info("MQTT event MQTT_EVENT_DISCONNECTED");
      break;
    case MQTT_EVENT_SUBSCRIBED:
      Logger.Info("MQTT event MQTT_EVENT_SUBSCRIBED");
      break;
    case MQTT_EVENT_UNSUBSCRIBED:
      Logger.Info("MQTT event MQTT_EVENT_UNSUBSCRIBED");
      break;
    case MQTT_EVENT_PUBLISHED:
      Logger.Info("MQTT event MQTT_EVENT_PUBLISHED");
      break;
    case MQTT_EVENT_DATA:
      Logger.Info("MQTT event MQTT_EVENT_DATA");

      for (i = 0; i < (INCOMING_DATA_BUFFER_SIZE - 1) && i < event->topic_len; i++) {
        incoming_data[i] = event->topic[i];
      }
      incoming_data[i] = '\0';
      Logger.Info("Topic: " + String(incoming_data));

      for (i = 0; i < (INCOMING_DATA_BUFFER_SIZE - 1) && i < event->data_len; i++) {
        incoming_data[i] = event->data[i];
      }
      incoming_data[i] = '\0';
      Logger.Info("Data: " + String(incoming_data));

      break;
    case MQTT_EVENT_BEFORE_CONNECT:
      Logger.Info("MQTT event MQTT_EVENT_BEFORE_CONNECT");
      break;
    default:
      Logger.Error("MQTT event UNKNOWN");
      break;
  }

#if defined(ESP_ARDUINO_VERSION_MAJOR) && ESP_ARDUINO_VERSION_MAJOR >= 3
#else   // ESP_ARDUINO_VERSION_MAJOR
  return ESP_OK;
#endif  // ESP_ARDUINO_VERSION_MAJOR
}

static void initializeIoTHubClient() {
  az_iot_hub_client_options options = az_iot_hub_client_options_default();
  options.user_agent = AZ_SPAN_FROM_STR(AZURE_SDK_CLIENT_USER_AGENT);

  if (az_result_failed(az_iot_hub_client_init(
        &client,
        az_span_create((uint8_t*)host, strlen(host)),
        az_span_create((uint8_t*)device_id, strlen(device_id)),
        &options))) {
    Logger.Error("Failed initializing Azure IoT Hub client");
    return;
  }

  size_t client_id_length;
  if (az_result_failed(az_iot_hub_client_get_client_id(
        &client, mqtt_client_id, sizeof(mqtt_client_id) - 1, &client_id_length))) {
    Logger.Error("Failed getting client id");
    return;
  }

  if (az_result_failed(az_iot_hub_client_get_user_name(
        &client, mqtt_username, sizeofarray(mqtt_username), NULL))) {
    Logger.Error("Failed to get MQTT clientId, return code");
    return;
  }

  Logger.Info("Client ID: " + String(mqtt_client_id));
  Logger.Info("Username: " + String(mqtt_username));
}

static int initializeMqttClient() {
#ifndef IOT_CONFIG_USE_X509_CERT
  if (sasToken.Generate(SAS_TOKEN_DURATION_IN_MINUTES) != 0) {
    Logger.Error("Failed generating SAS token");
    return 1;
  }
#endif

  esp_mqtt_client_config_t mqtt_config;
  memset(&mqtt_config, 0, sizeof(mqtt_config));

#if defined(ESP_ARDUINO_VERSION_MAJOR) && ESP_ARDUINO_VERSION_MAJOR >= 3
  mqtt_config.broker.address.uri = mqtt_broker_uri;
  mqtt_config.broker.address.port = mqtt_port;
  mqtt_config.credentials.client_id = mqtt_client_id;
  mqtt_config.credentials.username = mqtt_username;

#ifdef IOT_CONFIG_USE_X509_CERT
  LogInfo("MQTT client using X509 Certificate authentication");
  mqtt_config.credentials.authentication.certificate = IOT_CONFIG_DEVICE_CERT;
  mqtt_config.credentials.authentication.certificate_len = (size_t)sizeof(IOT_CONFIG_DEVICE_CERT);
  mqtt_config.credentials.authentication.key = IOT_CONFIG_DEVICE_CERT_PRIVATE_KEY;
  mqtt_config.credentials.authentication.key_len = (size_t)sizeof(IOT_CONFIG_DEVICE_CERT_PRIVATE_KEY);
#else  // Using SAS key
  mqtt_config.credentials.authentication.password = (const char*)az_span_ptr(sasToken.Get());
#endif

  mqtt_config.session.keepalive = 30;
  mqtt_config.session.disable_clean_session = 0;
  mqtt_config.network.disable_auto_reconnect = false;
  mqtt_config.broker.verification.certificate = (const char*)ca_pem;
  mqtt_config.broker.verification.certificate_len = (size_t)ca_pem_len;
#else  // ESP_ARDUINO_VERSION_MAJOR
  mqtt_config.uri = mqtt_broker_uri;
  mqtt_config.port = mqtt_port;
  mqtt_config.client_id = mqtt_client_id;
  mqtt_config.username = mqtt_username;

#ifdef IOT_CONFIG_USE_X509_CERT
  Logger.Info("MQTT client using X509 Certificate authentication");
  mqtt_config.client_cert_pem = IOT_CONFIG_DEVICE_CERT;
  mqtt_config.client_key_pem = IOT_CONFIG_DEVICE_CERT_PRIVATE_KEY;
#else  // Using SAS key
  mqtt_config.password = (const char*)az_span_ptr(sasToken.Get());
#endif

  mqtt_config.keepalive = 30;
  mqtt_config.disable_clean_session = 0;
  mqtt_config.disable_auto_reconnect = false;
  mqtt_config.event_handle = mqtt_event_handler;
  mqtt_config.user_context = NULL;
  mqtt_config.cert_pem = (const char*)ca_pem;
#endif  // ESP_ARDUINO_VERSION_MAJOR

  mqtt_client = esp_mqtt_client_init(&mqtt_config);

  if (mqtt_client == NULL) {
    Logger.Error("Failed creating mqtt client");
    return 1;
  }

#if defined(ESP_ARDUINO_VERSION_MAJOR) && ESP_ARDUINO_VERSION_MAJOR >= 3
  esp_mqtt_client_register_event(mqtt_client, MQTT_EVENT_ANY, mqtt_event_handler, NULL);
#endif  // ESP_ARDUINO_VERSION_MAJOR

  esp_err_t start_result = esp_mqtt_client_start(mqtt_client);

  if (start_result != ESP_OK) {
    Logger.Error("Could not start mqtt client; error code:" + start_result);
    return 1;
  } else {
    Logger.Info("MQTT client started");
    return 0;
  }
}

static uint32_t getEpochTimeInSecs() {
  return (uint32_t)time(NULL);
}

static void establishConnection() {
  connectToWiFi();
  initializeTime();
  initializeIoTHubClient();
  (void)initializeMqttClient();
}

static void generateTelemetryPayload() {
  JSONVar info;
  // Obtiene la fecha y hora
  t = timeClient.getEpochTime();
  // Extrae la fecha precisa
  dayStamp = String(year(t)) + '-' + String(month(t)) + '-' + String(day(t));
  timeStamp = timeClient.getFormattedTime();

  ///************************************  Write Sensors Data ************************************/
  //telemetry_payload = "{ \"MAC\": " + mac +
  //                    ", \"Fecha\": " + dayStamp +
  //                    ", \"Hora\": " + timeStamp +
  //                    ", \"Lugar\": " + ubicacion +
  //                    ", \"Sensor\": \"0\""
  //                    ", \"Temperatura\": \"" + String(temperatura) + "\"" +
  //                    ", \"Sensor\": \"1\""
  //                    ", \"Humedad\": \"" + String(humedad) + "\"" +
  //                    ", \"Sensor\": \"2\""
  //                    ", \"ValorGas\": \"" + String(gas) + "\" }";
  ///*********************************************************************************************/

  info["MAC"] = mac;
  info["Fecha"] = dayStamp;
  info["Hora"] = timeStamp;
  info["Lugar"] = ubicacion;
  info["SensorT"] = "0";
  info["Temperatura"] = String(temperatura);
  info["SensorH"] = "1";
  info["Humedad"] = String(humedad);
  info["SensorG"] = "2";
  info["ValorGas"] = String(gas);

  telemetry_payload = JSON.stringify(info);
  Serial.println(telemetry_payload);
}

static void sendTelemetry() {
  Logger.Info("Sending telemetry ...");

  if (az_result_failed(az_iot_hub_client_telemetry_get_publish_topic(
        &client, NULL, telemetry_topic, sizeof(telemetry_topic), NULL))) {
    Logger.Error("Failed az_iot_hub_client_telemetry_get_publish_topic");
    return;
  }

  //generateTelemetryPayload();

  if (esp_mqtt_client_publish(
        mqtt_client,
        telemetry_topic,
        (const char*)telemetry_payload.c_str(),
        telemetry_payload.length(),
        MQTT_QOS1,
        DO_NOT_RETAIN_MSG)
      == 0) {
    Logger.Error("Failed publishing");
  } else {
    Logger.Info("Message published successfully");
    Serial.println(telemetry_payload);
  }
}

static void sendToDB() {
  HTTPClient http;
  http.begin(servidorDB.c_str());                       // Specify the URL
  int httpResponseCode = http.POST(telemetry_payload);  // Perform the POST request

  if (httpResponseCode > 0) {
    Serial.print("HTTP Response code: ");
    Serial.println(httpResponseCode);
    String payload = http.getString();  // Get the response payload
    Serial.println("Payload: ");
    Serial.println(payload);
  } else {
    Serial.print("Error on HTTP request: ");
    Serial.println(httpResponseCode);
  }
  http.end();  // Free resources
}


void setup() {
  Serial.begin(9600);
  // Conexión
  establishConnection();

  // Preparando sensor DHT
  Serial.println(F("DHTxx test!"));
  dht.begin();

  // Preparando sensor MQ2
  Serial.println(F("Calentando el sensor MQ2"));
  delay(20000);  // Esperar a que se caliente
  // De ser posible, dejarlo calentar 15 mins
  // antes de comenzar a tomar lecturas

  // Preparando conexión a servidor NTP
  // para tener fecha y hora precisas
  timeClient.begin();
  timeClient.setTimeOffset(GMT_OFFSET_SECS);
}

void loop() {
  server.handleClient();

  humedad = dht.readHumidity();
  temperatura = dht.readTemperature();
  gas = analogRead(MQ2PIN);

  //while (!timeClient.update()) {
  //  timeClient.forceUpdate();
  //}
  timeClient.update();

  generateTelemetryPayload();

  sendTelemetry();
  sendToDB();

  // DESCOMENTAR AL CONECTAR SENSORES !!
  if (isnan(humedad) || isnan(temperatura)) {
    Serial.println(F("Fallo en la lectura del sensor DHT!"));
    return;
  }
  if (gas == 0) {
    Serial.println(F("Fallo en la lectura del sensor MQ2!"));
    return;
  }

  delay(TELEMETRY_FREQUENCY_MILLISECS);
}
