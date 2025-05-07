'''Equipo
    - Fernando de Jesus Barron Mojica 
    - Alan Jared Perez Soto
    - Marcos Eduardo Hernandez Moreno
    
    ESPECIFICACIONES: Codigo escrito para la placa ESP32-CAM, el cual permite capturar imagenes y enviarlas 
    a un servidor HTTP.
    El servidor HTTP se ejecuta en la misma placa ESP32-CAM y permite acceder a las imagenes capturadas a 
    traves de un navegador web.
    El servidor HTTP escucha en el puerto 80 y responde a las peticiones GET para la ruta /foto.jpg.
    El servidor HTTP responde con la imagen capturada en formato JPEG.
    El servidor HTTP responde con un error 404 si la ruta no es /foto.jpg.
    El servidor HTTP responde con un error 500 si no se pudo capturar la imagen.'''

import network
import socket
import camera
import time

# Conectar WiFi
def conectar_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Conectando a WiFi...")
        wlan.connect(ssid, password)
        timeout = 10
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1
    print("✅ WiFi conectado:", wlan.ifconfig()[0])

conectar_wifi('INFINITUMB6C2_2.4', '4021131201')

# Inicializar cámara
camera.init(0, format=camera.JPEG)
camera.framesize(camera.FRAME_QVGA)  # 320x240

# Servidor HTTP
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)
print("🌐 Servidor disponible. Accede a /foto.jpg para capturar imagen")

while True:
    cl, addr = s.accept()
    print('📡 Cliente conectado desde', addr)
    req = cl.recv(1024)

    if b"GET /foto.jpg" in req:
        img = camera.capture()
        if img:
            cl.send(b"HTTP/1.1 200 OK\r\nContent-Type: image/jpeg\r\n\r\n")
            cl.send(img)
        else:
            cl.send(b"HTTP/1.1 500 Internal Server Error\r\n\r\nNo se pudo capturar.")
    else:
        cl.send(b"HTTP/1.1 404 Not Found\r\n\r\n")

    cl.close()

