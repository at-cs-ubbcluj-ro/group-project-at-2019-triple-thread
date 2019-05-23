import time
from datetime import datetime

import PIL
import cv2
import numpy as np
from PIL import Image
from pytesseract import pytesseract
from skimage import io

from firebase.firebase_admin import FirebaseAdmin
from letter_recognition.PredictLP import PredictLP
from main.sim_server import SimulatorServer
from ocr.MSERWrapper import MSER_Segmentation
from ocr.PlateProcess import LPP
import tensorflow as tf

from yolo.YOLOWrapper import YOLOWrapper
from yolo.darknet import performDetect, detect, netMain, metaMain

'''
llp = LPP()
llp.run("saved/plate3.jpeg")
'''
'''
mesr = MSER_Segmentation("../saved/plate1.jpeg")


print("started")
# Run tesseract OCR on image
text = pytesseract.image_to_string(Image.open("../saved/plate3.jpeg"))
print(text)
'''
import time


#test server simulator
predictor = PredictLP()
server_sim = SimulatorServer("/demo", predictor)
start = time.time()
no_images = server_sim.run()
end = time.time()
print("processing "+str(no_images)+" in:"+str(end-start))
"""
fb_admin = FirebaseAdmin()
user_id = "1johKUqM3WMSUMHqBz9YyPrO3x63"
LP = "BV10ZR"
fb_admin.save_record(LP, user_id)
"""
