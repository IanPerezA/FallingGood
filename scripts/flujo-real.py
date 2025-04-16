import time
import subprocess
import paho.mqtt.client as mqtt
from gpiozero import DigitalInputDevice
from pathlib import Path
from datetime import datetime

# 🔹 CONFIGURACIÓN
SENSOR_SONIDO_GPIO = 17
CARPETA_IMAGENES = Path(__file__).parent / "img"  # Carpeta relativa al script
TIEMPO_ESPERA_ENTRE_CAPTURAS = 5
MQTT_BROKER = "a26hdnhnbzgxeh-ats.iot.us-east-2.amazonaws.com"  # Tu endpoint MQTT
MQTT_PORT = 8883
MQTT_TOPIC = "fall/detection"  # Tema MQTT para la detección de caídas

# 🔹 INICIALIZAR SENSOR Y CLIENTE MQTT
sensor_sonido = DigitalInputDevice(SENSOR_SONIDO_GPIO)

client = mqtt.Client()
client.tls_set()  # Si necesitas TLS
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()  # Iniciar loop de MQTT

# 🔹 FUNCIÓN PARA CAPTURAR IMAGEN
def capturar_imagen():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = CARPETA_IMAGENES / f"captura_{timestamp}.jpg"

    print(f"📸 Capturando imagen: {output_file.name}")
    try:
        subprocess.run([
            "libcamera-still",
            "-o", str(output_file),
            "-t", "1000",
            "--width", "1280",
            "--height", "720",
            "-n"
        ], check=True)
        print(f"✅ Imagen guardada en: {output_file}")
        # Publicar mensaje MQTT indicando que se capturó una imagen
        client.publish(MQTT_TOPIC, f"Imagen capturada: {output_file.name}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al capturar imagen: {e}")

# 🔹 BUCLE PRINCIPAL
print("🔊 Esperando sonidos fuertes...")

try:
    while True:
        if sensor_sonido.value == 1:
            print("🚨 ¡Sonido fuerte detectado!")
            capturar_imagen()
            # Publicar mensaje MQTT indicando que se detectó el sonido
            client.publish(MQTT_TOPIC, "¡Sonido fuerte detectado!")
            time.sleep(TIEMPO_ESPERA_ENTRE_CAPTURAS)
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n⏹️ Programa terminado.")
    client.loop_stop()  # Detener el loop MQTT
