# -*- coding: utf-8 -*-
"""Klasifikasi Kendaraan Submission.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1YOLtIWUq-h1BVCUCivUrLHJvwSwZXQec
"""

#Dependecies
import os
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
import shutil
from PIL import Image
from keras.preprocessing.image import ImageDataGenerator

#Kelas Kendaraan
Kendaraan = os.path.join('/content/drive/My Drive/Dicoding/Submission/Submission_3/Dataset/train')
print(os.listdir(Kendaraan))

"""Sumber Data : https://www.kaggle.com/abtabm/multiclassimagedatasetairplanecar"""

#Menunjukkan Size Gambar
total = 0
Jenis = os.listdir(Kendaraan)

for i in Jenis:
  dir = os.path.join(Kendaraan, i)
  y = len(os.listdir(dir))
  print(i + ':', y)
  total = total + y

  image_name = os.listdir(dir)
  for j in range(5):
    image_path = os.path.join(dir, image_name[j])
    image = Image.open(image_path)
    print('#', image.size)
  print('_________________')

print('\nTotal :', total)

"""Size Berbeda-beda

"""

#Menunjukkan Gambar Secara Acak
fig, ax = plt.subplots(2,2, figsize=(15,15))
fig.suptitle('Gambar Random', fontsize = 26)
Kendaraan_Urut = sorted(Jenis)
Kendaraan_id = 0

for i in range(2):
  for j in range(2):
    try:
      Kendaraan_terpilih = Kendaraan_Urut[Kendaraan_id]
      Kendaraan_id += 1
    except:
      break
    if Kendaraan_terpilih == '.TEMP':
      continue
    Gambar_Kendaraan_terpilih = os.listdir(os.path.join(Kendaraan,Kendaraan_terpilih))
    Gambar_Kendaraan_random = np.random.choice(Gambar_Kendaraan_terpilih)
    image = plt.imread(os.path.join(Kendaraan, Kendaraan_terpilih,Gambar_Kendaraan_random))
    ax[i][j].imshow(image)
    ax[i][j].set_title(Kendaraan_terpilih, pad = 10, fontsize = 25)
plt.setp(ax, xticks=[], yticks=[])
plt.show()

#Augmentasi Gambar
Datagen_train = ImageDataGenerator(
    width_shift_range = 0.2,
    height_shift_range = 0.2,
    rotation_range = 50,
    rescale = 1/255,
    horizontal_flip = True,
    shear_range = 0.2,
    zoom_range=0.2,
    fill_mode = 'nearest',
    validation_split = 0.2
)

#Mensplit Dataset
batch_size = 256

Data_train = Datagen_train.flow_from_directory(
    Kendaraan,
    target_size = (100,100),
    batch_size = batch_size,
    class_mode = 'categorical',
    subset = 'training')
Data_val = Datagen_train.flow_from_directory(
    Kendaraan,
    target_size = (100,100),
    batch_size = batch_size,
    class_mode = 'categorical',
    subset = 'validation')

#Membuat Model CNN
Model = tf.keras.models.Sequential([
    tf.keras.layers.Conv2D(64, (3,3), activation='relu', input_shape=(100, 100, 3)),
    tf.keras.layers.MaxPooling2D(2, 2),
    tf.keras.layers.Conv2D(128, (3,3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.Conv2D(256, (3,3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.Conv2D(128, (3,3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.Conv2D(64, (3,3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dropout(0.5), 
    tf.keras.layers.Dense(512, activation='relu'),
    tf.keras.layers.Dense(3, activation='softmax')
])

Model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics = ['accuracy'])

Model.summary()

#Optimizer
Optimizer = tf.keras.optimizers.Adam(learning_rate=1e-8)

#Callback dengan Target 92%
class CallbackIni(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('accuracy')>0.92 and logs.get('val_accuracy')>0.92):
      print("\Akurasi telah diatas 92%")
      self.model.stop_training = True

callbacks = CallbackIni()

#Train Model
history = Model.fit(Data_train, 
                    epochs = 40, 
                    steps_per_epoch = Data_train.samples // batch_size,
                    validation_data = Data_val, 
                    validation_steps = Data_val.samples // batch_size,
                    verbose = 2,
                    callbacks = [callbacks])

"""Akurasi Train Dataset 0.8862, Akurasi Val Dataset 0.8750"""

#Plot Progress dari Train Model

#Akurasi
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'val'], loc='lower right')
plt.show()

#Loss
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'val'], loc='upper right')
plt.show()

#convert ke TF-LITE
converter = tf.lite.TFLiteConverter.from_keras_model(Model)
tflite_model = converter.convert()

with tf.io.gfile.GFile('model.tflite', 'wb') as f:
  f.write(tflite_model)