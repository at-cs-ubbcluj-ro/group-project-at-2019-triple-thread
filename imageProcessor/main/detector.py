import os
import time

import cv2

from ocr.MSERWrapper import MSER_Segmentation
from ocr.MSER_strategy import MSER_Strategy
from ocr.Otsu_Strategy import Otsu_Strategy
from ocr.PlateProcess import LPP
from yolo.YOLOWrapper import YOLOWrapper
from ocr.context import Context

from datetime import datetime

ROOT_DIR = os.path.split(os.environ['VIRTUAL_ENV'])[0]


class Detector:
    def __init__(self, predictor):
        # llp = LPP()
        # llp.run(file_name="plate3.jpg")
        self.yolo = YOLOWrapper()
        self.yolo = self.yolo.add_config_path("/yolo/cfg/yolo-obj3.cfg")
        self.yolo = self.yolo.add_meta_path("/yolo/cfg/obj3.data")
        self.yolo = self.yolo.add_weight_path("/yolo/6k_Cluster_3OBJ_04.weights")
        self.yolo = self.yolo.build()
        self.predictor = predictor

        #self.yolo = YOLOWrapper().build()
        self.save_number = 1

        # if there are already some files saved search for the last one and take its number+1
        filenames = sorted(os.listdir(ROOT_DIR+"/saved"))
        if len(filenames) > 0:
            import re
            for filename in filenames:
                match = re.search('plate(\d+)', filename)
                if match:
                    self.save_number = int(match.group(1))
                    self.save_number += 1

    def detect(self, current_img_number=1, full_path="", debug=True):
        if full_path == "":
            image_path = "/taken/img" + str(current_img_number) + ".jpeg"
        else:
            image_path = full_path

        detections = self.yolo.perform_detection(image_path)
        if debug:
            print("found " + str(len(detections)) + " cars.")

        for d in detections:
            print(" found at: " + str(datetime.now()))

            # print(" detection of:" + str(c))
            # print(" precision:" + str(p))

            cv2.imwrite(ROOT_DIR + "/saved/" + "car" + str(self.save_number) + ".jpeg", d["car"])
            cv2.imwrite(ROOT_DIR + "/saved/" + "plate" + str(self.save_number) + ".jpeg", d["plate"])

            print("segmentation and letter recognition on:\n\t " + str(ROOT_DIR + "/saved/" + "plate" + str(self.save_number) + ".jpeg"))

            img_path = ROOT_DIR + "/saved/plate" + str(self.save_number) + ".jpeg"

            concrete_strategy_mser = MSER_Strategy()
            context = Context(concrete_strategy_mser)
            result = context.context_segemnt(img_path, self.predictor)

            # old call, before strategy pattern
            # mesr = MSER_Segmentation(img_path, predictor=self.predictor)

            # go to the next plate number
            self.save_number += 1

            return result

