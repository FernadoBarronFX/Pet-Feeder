from flask import Flask, render_template, Response
import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

app = Flask(__name__)
modelo = load_model('modelo/modelo_zuky.h5')
image_size = (224, 224)
cap = cv2.VideoCapture(0)

def gen_frames():
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        imagen = cv2.resize(frame, image_size)
        imagen_rgb = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
        imagen_pre = preprocess_input(imagen_rgb)
        imagen_pre = np.expand_dims(imagen_pre, axis=0)

        pred = modelo.predict(imagen_pre)[0][0]
        if pred >= 0.5:
            texto = "¡Es Zuky!"
            color = (0, 255, 0)
        else:
            texto = "Otro perro"
            color = (0, 0, 255)

        cv2.putText(frame, texto, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return '<h1>Reconocimiento de Zuky</h1><img src="/video_feed">'
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
