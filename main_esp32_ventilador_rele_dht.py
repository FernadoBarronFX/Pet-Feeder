''' Equipo:
    - Fernando de Jesus Barron Mojica
    - Alan Jared Perez Soto
    - Marcos Eduardo Hernandez Moreno
    
    ESPECIFICACIONES: Codigo escrito en micropython para el ESP32, en el cual se controla un ventilador,
    un rele y un sensor DHT11.
    El sistema se conecta a Firebase y tiene dos modos de operación: automático y manual.
    En modo automático, el sistema enciende el ventilador si la temperatura supera un umbral definido.
    En modo manual, el sistema enciende el ventilador al recibir un comando remoto desde Firebase.
    El sistema se conecta a una red WiFi y utiliza un rele para controlar el ventilador.
    El código incluye funciones para medir la temperatura con el sensor DHT11 y controlar el rele.
    El sistema sube la temperatura medida a Firebase y actualiza el estado del ventilador.'''
    
    
import machine
import time
import dht
import ufirebase

# Pines
PIN_DHT = 14
PIN_RELE = 26

# Histéresis
UMBRAL_ENCENDER = 31
UMBRAL_APAGAR = 29

# Inicialización
sensor = dht.DHT11(machine.Pin(PIN_DHT))
rele = machine.Pin(PIN_RELE, machine.Pin.OUT)
rele.on()  # APAGADO por defecto
estado_actual = False

# WiFi
import network
def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect('INFINITUMB6C2_2.4', '4021131201')
        timeout = 10
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1
    if wlan.isconnected():
        print("✅ WiFi conectado:", wlan.ifconfig()[0])
    else:
        print("❌ No se pudo conectar a WiFi")

conectar_wifi()

# Firebase
ufirebase.setURL("https://pet---feeder-default-rtdb.firebaseio.com/")

def subir_temperatura(temp):
    ufirebase.put("sensor/temperatura", temp, bg=False)
    print("🌡 Temperatura subida:", temp)

def leer_modo():
    ufirebase.get("control/ventilador_modo", "modo")
    return str(ufirebase.modo).lower()

def leer_manual():
    ufirebase.get("control/ventilador_manual", "manual")
    return str(ufirebase.manual).lower() == "true"

def actualizar_estado(encendido):
    ufirebase.put("control/ventilador_estado", "ON" if encendido else "OFF", bg=False)
    print("🔄 Ventilador", "ENCENDIDO" if encendido else "APAGADO")

# Bucle principal
while True:
    try:
        sensor.measure()
        temp = sensor.temperature()
        subir_temperatura(temp)

        modo = leer_modo()
        print("🌀 Modo ventilador desde Firebase:", modo)
        encender = False

        if modo == "automatico":
            print("🧠 MODO AUTOMÁTICO ACTIVADO")

            if temp >= UMBRAL_ENCENDER:
                if not estado_actual:
                    print("🔥 Temperatura alta (", temp, "°C) — Encendiendo ventilador")
                    rele.off()
                    estado_actual = True
                    actualizar_estado(True)
                else:
                    print("✅ Ventilador ya encendido (", temp, "°C)")

            elif temp <= UMBRAL_APAGAR:
                if estado_actual:
                    print("🌡 Temperatura bajó (", temp, "°C) — Apagando ventilador")
                    rele.on()
                    estado_actual = False
                    actualizar_estado(False)
                else:
                    print("✅ Ventilador ya apagado (", temp, "°C)")

            else:
                print("↔️ Zona neutra, manteniendo estado (", temp, "°C)")

        elif modo == "manual":
            print("🧠 MODO MANUAL ACTIVADO")
            encender = leer_manual()

            if encender and not estado_actual:
                print("🟢 Encendiendo ventilador manualmente")
                rele.off()
                estado_actual = True
                actualizar_estado(True)

            elif not encender and estado_actual:
                print("🔴 Apagando ventilador manualmente")
                rele.on()
                estado_actual = False
                actualizar_estado(False)

            else:
                print("↔️ Mando manual sin cambios")

    except Exception as e:
        print("❌ Error:", e)

    time.sleep(3)


