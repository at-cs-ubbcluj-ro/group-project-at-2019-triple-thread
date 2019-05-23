import os
import re

import cv2
import numpy as np
import imutils
from skimage import img_as_ubyte

from letter_recognition.PredictLP import PredictLP

ROOT_DIR = os.path.split(os.environ['VIRTUAL_ENV'])[0]


class Otsu_Segmentation:
    '''
        license plate processing
        input: path to a image with a plate
        output: the licence plate is saved in plateNumber(can be taken with get_lp())
    '''
    def __init__(self, file_name="../saved/plate2.jpeg", visu=False, predictor=None):
        self.palteNo = re.findall("\d+(?=\.\w+$)", file_name)[0]

        if predictor is None:
            # load the predictor only once if it was not loaded previously
            self.predictor = PredictLP()
        else:
            self.predictor = predictor
        self.plateNumber = ""
        self.visu = visu    # true or false, flag that helps for debugging and presentation
        self.startSegmentation(file_name)



    def startSegmentation(self, file_name):
        gamma = 1.2
        plate = cv2.imread(file_name, 0)                      # read the image
        plate = imutils.resize(plate, height=100, width=230)  # resize the image
        if self.visu:
            cv2.imshow("original", plate)

        plate = Otsu_Segmentation.pow_law_transformation(plate, gamma)   # enhance
        if self.visu:
            cv2.imshow("pow transofrmed", plate)

        # Otsu's thresholding
        ret3, otsu_bin_img = cv2.threshold(plate, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        if self.visu:
            cv2.imshow("otsu_only", otsu_bin_img)

        otsu_bin_img = cv2.bitwise_not(otsu_bin_img)
        # segement the characters from the binary image
        self.segment_chars(otsu_bin_img)

        if self.visu:
            cv2.waitKey()

        print("detected LP:" + self.plateNumber)

        # track detections result in a txt file
        with open(ROOT_DIR+"\\plates.txt", "a") as myfile:
            myfile.write(file_name + " " + self.plateNumber + "\n")

    def get_lp(self):
        return self.plateNumber

    def segment_chars(self, image):
        ret, labels = cv2.connectedComponents(image)

        if self.visu:
            Otsu_Segmentation.imshow_components(0, labels)
        try:
            os.mkdir(ROOT_DIR + "\chars\plate" + self.palteNo)
            print("created dir " + ROOT_DIR + "chars\plate" + self.palteNo)
        except:
            pass

        symbols = []
        for crt in range(1, ret):
            oneSymbol = np.where(labels == crt, len(labels), 0)

            first_non_empty_col = Otsu_Segmentation.first_nonzero(oneSymbol, axis=0)

            # delete empty rows and columns
            data = np.delete(oneSymbol, np.where(~oneSymbol.any(axis=0))[0], axis=1)
            data = data[~np.all(data == 0, axis=1)]

            symbols.append((data, first_non_empty_col))

        # sort the symbols based on the number of empty columns from left to right
        symbols = sorted(symbols, key=lambda x: x[1])

        for crt in range(len(symbols)):
            self.imshow_components2(crt, symbols[crt][0], save=True)

    @staticmethod
    def imshow_components(crt, labels):
        # Map component labels to hue val
        label_hue = np.uint8(179 * labels / np.max(labels))
        blank_ch = 255 * np.ones_like(label_hue)
        labeled_img = cv2.merge([label_hue, blank_ch, blank_ch])

        # cvt to BGR for display
        labeled_img = cv2.cvtColor(labeled_img, cv2.COLOR_HSV2BGR)

        # set bg label to black
        labeled_img[label_hue == 0] = 0
        cv2.imshow("comonents", labeled_img)

    def imshow_components2(self, crt, labels, save=False):
        # Map component labels to hue val
        label_hue = np.uint8(179 * labels / np.max(labels))
        blank_ch = 255 * np.ones_like(label_hue)
        labeled_img = cv2.merge([label_hue, blank_ch, blank_ch])

        if not (15 < labeled_img.shape[0] < 50) or not(labeled_img.shape[1] < 100):
            # discard small images that are not symbols for sure, just some failures
            # print(str(labeled_img.shape[0])+" "+str(labeled_img.shape[1]))
            return

        if labeled_img.shape[0] < 50:
            # cvt to BGR for display sequence of symbols, each with one color
            labeled_img = cv2.cvtColor(labeled_img, cv2.COLOR_BGR2GRAY)
        else:
            # cvt to grayscale for display one symbol
            labeled_img = cv2.cvtColor(labeled_img, cv2.COLOR_HSV2BGR)

        # set bg label to black
        labeled_img[label_hue == 0] = 0

        # labeled_img = np.pad(labeled_img, [(40 - labeled_img.shape[0],), (40 - labeled_img.shape[1],)], mode='constant')

        if self.visu:
            cv2.imshow(str(crt), labeled_img)


        if save:
            cv2.imwrite(ROOT_DIR + "\\chars\\plate" + self.palteNo + "\\c" + str(crt) + ".jpeg", labeled_img)

        try:
            crt = int(crt)
            symbol = self.predictor.run("\\chars\\plate" + self.palteNo + "\\c" + str(crt) + ".jpeg")
            self.plateNumber = self.plateNumber + symbol
        except ValueError:
            pass

    @staticmethod
    def first_nonzero(arr, axis, invalid_val=-1):
        mask = arr != 0
        non_zero_indexes = np.where(mask.any(axis=axis), mask.argmax(axis=axis), invalid_val)
        mask = non_zero_indexes != -1
        return np.where(mask.any(axis=axis), mask.argmax(axis=axis), 0)

    @staticmethod
    def pow_law_transformation(gray_img_p, gamma):
        im_power_law_transformation = gray_img_p / 255.0
        im_power_law_transformation = cv2.pow(im_power_law_transformation, gamma)
        im_power_law_transformation = img_as_ubyte(im_power_law_transformation)
        return im_power_law_transformation
