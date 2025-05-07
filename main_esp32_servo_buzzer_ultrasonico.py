''' Equipo
    - Fernando de Jesus Barron Mojica 
    - Alan Jared Perez Soto
    - Marcos Eduardo Hernandez Moreno
    
    ESPECIFICACIONES: Codigo escrito en micropython para el ESP32, en el cual se controla un servo motor, 
    un zumbador activo y un sensor ultrasónico.
    El sistema se conecta a Firebase y tiene dos modos de operación: automático y manual.
    En modo automático, el sistema abre el recipiente si el plato está vacío (distancia menor a 
    un umbral definido).
    En modo manual, el sistema abre el recipiente al recibir un comando remoto desde Firebase.
    El sistema se conecta a una red WiFi y utiliza un zumbador para indicar el estado del recipiente.
    El código incluye funciones para medir la distancia con el sensor ultrasónico, controlar el servo 
    motor y activar el zumbador.'''

import network
import urequests as requests
import ujson as json
from machine import Pin, PWM, time_pulse_us
from time import sleep
import gc

# --- Configuración WiFi ---
def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("🔌 Conectando a WiFi...")
        
        '''wlan.connect('Alumnos-TecNM-D-UF')'''
        
        '''wlan.connect('Xiaomi de Fer', 'ferFX123')'''
        
        wlan.connect('INFINITUMB6C2_2.4', '4021131201')
        while not wlan.isconnected():
            sleep(1)
    print("✅ Conectado. IP:", wlan.ifconfig()[0])

# --- Sensor ultrasónico ---
TRIG = Pin(5, Pin.OUT)
ECHO = Pin(18, Pin.IN)

def medir_distancia():
    TRIG.off()
    sleep(0.002)
    TRIG.on()
    sleep(0.00001)
    TRIG.off()
    duracion = time_pulse_us(ECHO, 1, 30000)
    distancia_cm = (duracion / 2) * 0.0343
    return round(distancia_cm, 2)

# --- Servo motor ---
servo = PWM(Pin(17), freq=50)
DUTY_ABRIR = 120
DUTY_CERRAR = 40

def abrir_recipiente():
    servo.duty(DUTY_ABRIR)
    print("🔓 Abriendo recipiente")
    sleep(1)

def cerrar_recipiente():
    servo.duty(DUTY_CERRAR)
    print("🔒 Cerrando recipiente")
    sleep(0.5)

# --- Zumbador activo ---
zumbador = Pin(23, Pin.OUT)

def activar_zumbador():
    print("🔊 Zumbador activado")
    for _ in range(2):
        zumbador.on()
        sleep(1)
        zumbador.off()
        sleep(0.2)

# --- Firebase URLs ---
FIREBASE_URL = "https://pet---feeder-default-rtdb.firebaseio.com/control"
URL_ALIMENTAR = FIREBASE_URL + "/alimentar.json"
URL_MODO = FIREBASE_URL + "/modo.json"

def leer_comando_remoto():
    try:
        res = requests.get(URL_ALIMENTAR)
        if res.status_code == 200:
            valor = res.json()
            res.close()
            del res
            return valor == True
        res.close()
        del res
    except Exception as e:
        print("❌ Error leyendo alimentar:", e)
    return False

def reset_comando_remoto():
    try:
        res = requests.put(URL_ALIMENTAR, json=False)
        res.close()
        del res
    except Exception as e:
        print("❌ Error reseteando alimentar:", e)

def leer_modo():
    try:
        res = requests.get(URL_MODO)
        if res.status_code == 200:
            modo = res.json()
            res.close()
            del res
            return modo
        res.close()
        del res
    except Exception as e:
        print("❌ Error leyendo modo:", e)
    return "automatico"  # por defecto

# --- Umbral para plato vacío ---
UMBRAL_VACIO = 26  # cm

# --- Inicio del sistema ---
conectar_wifi()
cerrar_recipiente()

print("🤖 Sistema en funcionamiento...")

# --- Loop principal ---
while True:
    modo = leer_modo()
    distancia = medir_distancia()
    print("📏 Distancia:", distancia, "cm | Modo:", modo)

    if modo == "automatico" and distancia > UMBRAL_VACIO:
        print("🍽 Modo automático: plato vacío.")
        activar_zumbador()
        abrir_recipiente()
        cerrar_recipiente()

    elif modo == "manual" and leer_comando_remoto():
        print("📦 Modo manual: comando remoto.")
        abrir_recipiente()
        cerrar_recipiente()
        reset_comando_remoto()

    gc.collect()
    sleep(3)
