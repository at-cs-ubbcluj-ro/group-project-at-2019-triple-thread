import os

from keras.models import load_model
from keras.preprocessing import image
import numpy as np
import cv2
import tensorflow as tf

ROOT_DIR = os.path.split(os.environ['VIRTUAL_ENV'])[0]
WEIGHTS = ROOT_DIR + r"\letter_recognition\weights.best.hdf5"


class PredictLP:
    '''
        takes a sequence of images with letters and predicts using CNN what is the licence plate number
        input: sequence of bw images
        output: string with the LP number
    '''

    def __init__(self):
        with tf.device("/cpu:0"):
            self.model = load_model(WEIGHTS)
        self.alpha_numeric = {0: "0", 1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9",
                              10: "A", 11: "B", 12: "C", 13: "D", 14: "E", 15: "F", 16: "G", 17: "H", 18: "I",
                              19: "J", 20: "K", 21: "L", 22: "M", 23: "N", 24: "O", 25: "P", 26: "Q", 27: "R",
                              28: "S", 29: "T", 30: "U", 31: "V", 32: "W", 33: "X", 34: "Y", 35: "Z"}



    def run(self, image_path="\\chars\\c1.jpeg"):
        image_path = ROOT_DIR + image_path

        test_image = image.load_img(image_path, target_size=(40, 40))
        test_image = image.img_to_array(test_image)
        test_image = cv2.cvtColor(test_image, cv2.COLOR_BGR2GRAY)
        test_image = np.expand_dims(test_image, axis=0)
        test_image = np.expand_dims(test_image, axis=0)

        # predict the result
        result = self.model.predict(test_image)
        print(self.alpha_numeric[np.argmax(result)])
        print(np.argmax(result))
        print("===========================")
        return self.alpha_numeric[np.argmax(result)]
