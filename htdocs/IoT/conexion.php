<?php
// Conexión segura a MySQL

ini_set('display_errors', 1);

try {
    // usar localhost SIEMPRE cuando es XAMPP
    $pdo = new PDO(
        "mysql:host=localhost;dbname=Reto;charset=utf8",
        "esp32",
        "ESP32-IoT-equipo1",
        [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION
        ]
    );

    echo "<h2>Conexión exitosa a MySQL</h2>";

} catch (PDOException $e) {
    echo "<h3>Error al conectar con la BD</h3>";
    echo "Error: " . $e->getMessage();
    exit;
}
?>
