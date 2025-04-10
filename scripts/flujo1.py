import tensorflow as tf
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

import time
import subprocess
from gpiozero import DigitalInputDevice
from pathlib import Path
from datetime import datetime

# CONFIGURACIÓN DEL MODELO
model_path = 'model.h5'  # Ruta al modelo guardado
img_height = 240
img_width = 320
class_names = ['lying', 'sitting', 'standing']

# Cargar el modelo
model = load_model(model_path)
print("Modelo cargado correctamente.")

def predict_class(img_path):
    """
    Recibe la ruta de una imagen, la procesa, realiza la predicción 
    y retorna la clase predicha junto con la confianza.
    """
    # Cargar y preprocesar la imagen
    img = image.load_img(img_path, target_size=(img_height, img_width))
    img_array = image.img_to_array(img)
    img_array = img_array / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    # Realizar la predicción
    predictions = model.predict(img_array)
    predicted_index = np.argmax(predictions[0])
    predicted_class = class_names[predicted_index]
    confidence = predictions[0][predicted_index]

    return predicted_class, confidence

# CONFIGURACIÓN DEL SENSOR Y CAPTURA 
SENSOR_SONIDO_GPIO = 17
CARPETA_IMAGENES = Path(__file__).parent / "img"  # Carpeta relativa al script
TIEMPO_ESPERA_ENTRE_CAPTURAS = 5  # Tiempo de espera en segundos entre capturas

# Crear carpeta si no existe
CARPETA_IMAGENES.mkdir(parents=True, exist_ok=True)

# Inicializar el sensor de sonido
sensor_sonido = DigitalInputDevice(SENSOR_SONIDO_GPIO)

def capturar_imagen():
    """
    Captura una imagen utilizando libcamera-still y retorna la ruta del archivo.
    """
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
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al capturar imagen: {e}")
        return None

# BUCLE PRINCIPAL 
print("🔊 Esperando sonidos fuertes...")

try:
    while True:
        # Si se detecta un sonido fuerte
        if sensor_sonido.value == 1:
            print("🚨 ¡Sonido fuerte detectado!")
            imagen_capturada = capturar_imagen()
            if imagen_capturada:
                # Realizar la predicción sobre la imagen capturada
                clase, confianza = predict_class(str(imagen_capturada))
                print(f"🔍 Predicción: {clase} con una confianza de {confianza:.2f}")
            # Esperar un tiempo determinado antes de la siguiente captura
            time.sleep(TIEMPO_ESPERA_ENTRE_CAPTURAS)
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n⏹️ Programa terminado.")
