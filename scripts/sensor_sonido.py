from gpiozero import DigitalInputDevice
from time import sleep

sensor_sonido = DigitalInputDevice(17)

estado_anterior = sensor_sonido.value  

print("Esperando sonidos...")

try:
    while True:
        estado_actual = sensor_sonido.value
        if estado_actual != estado_anterior:
            if estado_actual == 1:
                print("🔊 ¡Sonido detectado!")
            else:
                print("🔇 Silencio...")
            estado_anterior = estado_actual
        sleep(0.1)  

except KeyboardInterrupt:
    print("\nPrograma terminado.")
