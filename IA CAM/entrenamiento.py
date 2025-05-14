import os
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping

# Rutas
base_dir = '.'  # el punto indica "carpeta actual"
batch_size = 16
image_size = (224, 224)

# Generador de imágenes con aumento de datos
datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2,
    horizontal_flip=True,
    zoom_range=0.2
)

train_gen = datagen.flow_from_directory(
    base_dir,
    target_size=image_size,
    batch_size=batch_size,
    class_mode='binary',
    subset='training'
)

val_gen = datagen.flow_from_directory(
    base_dir,
    target_size=image_size,
    batch_size=batch_size,
    class_mode='binary',
    subset='validation'
)

# Cargar MobileNetV2 base sin la capa de salida
base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))

# Congelar pesos
base_model.trainable = False

# Añadir capas finales
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(64, activation='relu')(x)
output = Dense(1, activation='sigmoid')(x)
model = Model(inputs=base_model.input, outputs=output)

model.compile(optimizer=Adam(1e-4), loss='binary_crossentropy', metrics=['accuracy'])

# Entrenar
model.fit(
    train_gen,
    validation_data=val_gen,
    epochs=10,
    callbacks=[EarlyStopping(patience=2, restore_best_weights=True)]
)

# Guardar modelo
os.makedirs('IA CAM/modelo', exist_ok=True)
model.save('IA CAM/modelo/modelo_zuky.h5')
