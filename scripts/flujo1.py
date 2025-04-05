import time
import subprocess
from gpiozero import DigitalInputDevice
from pathlib import Path
from datetime import datetime

# 🔹 CONFIGURACIÓN
SENSOR_SONIDO_GPIO = 17
CARPETA_IMAGENES = Path(__file__).parent / "img"  # Carpeta relativa al script
TIEMPO_ESPERA_ENTRE_CAPTURAS = 5

# 🔹 Crear carpeta si no existe
CARPETA_IMAGENES.mkdir(parents=True, exist_ok=True)

# 🔹 INICIALIZAR SENSOR
sensor_sonido = DigitalInputDevice(SENSOR_SONIDO_GPIO)

# 🔹 FUNCIÓN PARA CAPTURAR IMAGEN
def capturar_imagen():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = CARPETA_IMAGENES / f"captura.jpg"

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
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al capturar imagen: {e}")

# 🔹 BUCLE PRINCIPAL
print("🔊 Esperando sonidos fuertes...")

try:
    while True:
        if sensor_sonido.value == 1:
            print("🚨 ¡Sonido fuerte detectado!")
            capturar_imagen()
            time.sleep(TIEMPO_ESPERA_ENTRE_CAPTURAS)
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n⏹️ Programa terminado.")
