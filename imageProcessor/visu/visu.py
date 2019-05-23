import os

import numpy as np

import cv2


ROOT_DIR = os.path.split(os.environ['VIRTUAL_ENV'])[0]

class Visu:
    def __init__(self):
        f = open(ROOT_DIR + "/tzutzu.jpeg", 'rb')
        img_bytes = f.read()
        f.close()
        img = cv2.imdecode(np.frombuffer(img_bytes, dtype='uint8'), 1)
        self.img = img

    def update_img(self, img_mat):
        self.img = img_mat

    def run_visu(self):
        while True:
            cv2.imshow('image', self.img)
            cv2.waitKey(5)
