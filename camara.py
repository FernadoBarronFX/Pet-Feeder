'''Equipo
    - Fernando de Jesus Barron Mojica 
    - Alan Jared Perez Soto
    - Marcos Eduardo Hernandez Moreno
    
    ESPECIFICACIONES: Codigo para la inicializacion de la ESP32-CAM
    '''

import esp32
import machine
import gc

try:
    import camera
except ImportError:
    print("❌ Módulo de cámara no disponible.")
    raise

def iniciar_camara():
    try:
        camera.deinit()
    except:
        pass

    camera.init(0, format=camera.JPEG)
    camera.framesize(camera.FRAME_QVGA)
    print("📷 Cámara inicializada.")
