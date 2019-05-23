import os

from keras.models import load_model
from keras.preprocessing import image
import numpy as np
import cv2
ROOT_DIR = os.path.split(os.environ['VIRTUAL_ENV'])[0]
WEIGHTS = ROOT_DIR + r"\letter_recognition\weights.best.hdf5"
model = load_model(WEIGHTS)

imagePath = ROOT_DIR + "\\chars\\c1.jpeg"
#imagePath = r"C:\Users\Stefan-PC\Documents\ubb\anul III\semestrul II\AT\imageServer\letter_recognition\English\Img\GoodImg\Bmp\Sample007\img007-00013.png"


test_image = image.load_img(imagePath, target_size=(40, 40))
test_image = image.img_to_array(test_image)
test_image = cv2.cvtColor(test_image, cv2.COLOR_BGR2GRAY)
test_image = np.expand_dims(test_image, axis=0)
test_image = np.expand_dims(test_image, axis=0)


# predict the result
result = model.predict(test_image)

print(result)
res = np.argmax(result)
print(res+1)
'''
k = 0
m = 0
for i in range(len(result[0])):
    if result[0][i] > m:
        m = result[0][i]
        k = i

print(k+1)
'''
