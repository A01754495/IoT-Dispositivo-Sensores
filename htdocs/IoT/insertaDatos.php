<?php
// Inserción segura de datos IoT del ESP32

include "conexion.php";

// 1. Leer JSON desde el ESP32
$json_string = file_get_contents('php://input');

// Debug opcional: ver JSON recibido
// file_put_contents("debug_log.txt", $json_string . "\n", FILE_APPEND);

// 2. Convertir a objeto
$datos = json_decode($json_string);

if (!$datos) {
    echo json_encode(["error" => "No se recibió JSON válido"]);
    exit;
}

// 3. Extraer valores
$mac         = $datos->MAC         ?? null;
$fecha       = $datos->Fecha       ?? null;
$hora        = $datos->Hora        ?? null;
$lugar       = $datos->Lugar       ?? null;
$temperatura = $datos->Temperatura ?? null;
$humedad     = $datos->Humedad     ?? null;
$gas         = $datos->ValorGas    ?? null;

// DEBUG para verificar que sí llegan valores
echo "MAC: $mac\n";
echo "Fecha: $fecha\n";
echo "Hora: $hora\n";
echo "Lugar: $lugar\n";
echo "Temperatura: $temperatura\n";
echo "Humedad: $humedad\n";
echo "Gas: $gas\n";

try {

    // Insertar TEMPERATURA
    $stmt = $pdo->prepare(
        "INSERT INTO Registro_temp (id_sensor, lugar, medida_temp, fecha, hora) 
         VALUES (?, ?, ?, ?, ?)"
    );
    $stmt->execute([0, $lugar, $temperatura, $fecha, $hora]);

    // Insertar HUMEDAD
    $stmt = $pdo->prepare(
        "INSERT INTO Registro_humedad (id_sensor, lugar, medida_humedad, fecha, hora) 
         VALUES (?, ?, ?, ?, ?)"
    );
    $stmt->execute([1, $lugar, $humedad, $fecha, $hora]);

    // Insertar GAS
    $stmt = $pdo->prepare(
        "INSERT INTO Registro_gas (id_sensor, lugar, medida_gas, fecha, hora) 
         VALUES (?, ?, ?, ?, ?)"
    );
    $stmt->execute([2, $lugar, $gas, $fecha, $hora]);

    echo "\nDatos insertados correctamente";

} catch (PDOException $e) {
    echo "\nError al insertar: " . $e->getMessage();
}

?>
