import tensorflow as tf
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# CONFIGURACIÓN
model_path = 'model.h5'
img_path = 'scripts/captura.jpg'  # Cambia esta ruta
img_height = 240
img_width = 320

# CARGAR MODELO
model = load_model(model_path)

# CLASES
class_names = ['lying', 'sitting', 'standing']

# CARGAR IMAGEN
img = image.load_img(img_path, target_size=(img_height, img_width))
img_array = image.img_to_array(img)
img_array = img_array / 255.0  
img_array = np.expand_dims(img_array, axis=0)

# PREDICCIÓN
predictions = model.predict(img_array)
predicted_index = np.argmax(predictions[0])
predicted_class = class_names[predicted_index]
confidence = predictions[0][predicted_index]

# RESULTADO
print(f"Predicción: {predicted_class} ({confidence*100:.2f}%)")