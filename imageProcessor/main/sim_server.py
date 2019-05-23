import cv2
import os

from firebase.firebase_admin import FirebaseAdmin
from main.detector import Detector

ROOT_DIR = os.path.split(os.environ['VIRTUAL_ENV'])[0]

class SimulatorServer:
    '''
        This class is meant for presenting the detection using yolo
        It simulates the pipeline of images sent on the socket
        It takes images from the data set and perform detection on them
    '''

    def __init__(self, directory, predictor):
        self.directory = directory
        self.detector = Detector(predictor)
        self.fb_admin = FirebaseAdmin()
        self.user_id = "1johKUqM3WMSUMHqBz9YyPrO3x63"


    def run(self):
        files = sorted(os.listdir(ROOT_DIR + self.directory))
        print("the list of images to be processed:" + str(files))
        counter = 0
        for file in files:
            counter += 1
            print("/" + self.directory + "/" + file)
            LP = self.detector.detect(full_path="/" + self.directory + "/" + file)
            self.fb_admin.save_record(LP, self.user_id)
        return counter