#import tensorflow as tf
import numpy as np
#from tensorflow.keras.models import load_model
#from tensorflow.keras.preprocessing import image

import time
import subprocess
from gpiozero import DigitalInputDevice
from pathlib import Path
from datetime import datetime
import json
import ssl
import paho.mqtt.client as mqtt
'''from model_test import predict_class 
resultado, confianza = predict_class("captura.jpg")
print(f"Predicción: {resultado} (Confianza: {confianza:.2f})")'''

# CONFIGURACIÓN DEL MODELO
model_path = 'model.h5'
img_height = 240
img_width = 320
class_names = ['lying', 'sitting', 'standing']
#model = load_model(model_path)

# CONFIGURACIÓN DEL SENSOR
SENSOR_SONIDO_GPIO = 17
CARPETA_IMAGENES = Path(__file__).parent / "img"
TIEMPO_ESPERA_ENTRE_CAPTURAS = 5
CARPETA_IMAGENES.mkdir(parents=True, exist_ok=True)
sensor_sonido = DigitalInputDevice(SENSOR_SONIDO_GPIO)

# CONFIGURACIÓN MQTT - AWS IoT Core
MQTT_ENDPOINT = "a26hdnhnbzgxeh-ats.iot.us-east-1.amazonaws.com"
MQTT_PORT = 8883
MQTT_TOPIC = "/deteccion/caida"
ROOT_CA = "/home/adrian/falling-good/config/nuevaIoT/connect/root-CA.crt"
CERT = "/home/adrian/falling-good/config/nuevaIoT/connect/fg_bueno.cert.pem"
PRIVATE_KEY = "/home/adrian/falling-good/config/nuevaIoT/connect/fg_bueno.private.key"

mqtt_client = mqtt.Client()
mqtt_client.tls_set(ca_certs=ROOT_CA,
                    certfile=CERT,
                    keyfile=PRIVATE_KEY,
                    tls_version=ssl.PROTOCOL_TLSv1_2)
mqtt_client.connect(MQTT_ENDPOINT, MQTT_PORT)

def capturar_imagen():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = CARPETA_IMAGENES / f"captura_{timestamp}.jpg"
    try:
        subprocess.run([
            "libcamera-still",
            "-o", str(output_file),
            "-t", "1000",
            "--width", "1280",
            "--height", "720",
            "-n"
        ], check=True)
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al capturar imagen: {e}")
        return None

def predict_class(img_path):
    img = image.load_img(img_path, target_size=(img_height, img_width))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    predictions = model.predict(img_array)
    predicted_index = np.argmax(predictions[0])
    predicted_class = class_names[predicted_index]
    confidence = predictions[0][predicted_index]
    return predicted_class, confidence

# BUCLE PRINCIPAL
print("🔊 Esperando sonidos fuertes...")

try:
    while True:
        if sensor_sonido.value == 1:
            print("🚨 ¡Sonido fuerte detectado!")
            imagen_capturada = capturar_imagen()
            if imagen_capturada:
                #clase, confianza = predict_class(str(imagen_capturada))

                clase, confianza = 'liying', 0.95  
                print(f"🔍 Predicción: {clase} con una confianza de {confianza:.2f}")

                payload = {
                    "clase": clase,
                    "confianza": round(float(confianza), 2),
                    "timestamp": datetime.now().isoformat()
                }

                mqtt_client.publish(MQTT_TOPIC, json.dumps(payload))
                print(f"📡 Publicado en {MQTT_TOPIC}: {payload}")

            time.sleep(TIEMPO_ESPERA_ENTRE_CAPTURAS)
        time.sleep(0.1)
except KeyboardInterrupt:
    print("🛑 Proceso detenido.")
