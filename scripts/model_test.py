import tensorflow as tf
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# CONFIGURACIÓN
model_path = 'model.h5'
img_height = 240
img_width = 320
class_names = ['lying', 'sitting', 'standing']

# MODELO
model = load_model(model_path)

def predict_class(img_path):
    # IMAGEN
    img = image.load_img(img_path, target_size=(img_height, img_width))
    img_array = image.img_to_array(img)
    img_array = img_array / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    # PREDICCIÓN
    predictions = model.predict(img_array)
    predicted_index = np.argmax(predictions[0])
    predicted_class = class_names[predicted_index]
    confidence = predictions[0][predicted_index]

    return predicted_class, confidence

resultado, confianza = predict_class("captura.jpg")
print(f"Predicción: {resultado} (Confianza: {confianza:.2f})")