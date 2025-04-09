from scripts.predict import predict_class

clase, confianza = predict_class('scripts/captura.jpg')
print(f"Predicción: {clase} ({confianza*100:.2f}%)")