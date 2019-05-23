import os
import re

import cv2
import imutils as imutils
import numpy as np
from skimage import img_as_ubyte, filters

from letter_recognition.PredictLP import PredictLP

ROOT_DIR = os.path.split(os.environ['VIRTUAL_ENV'])[0]


class MSER_Segmentation:
    '''
        license plate processing
        input: path to a image with a plate
        output: the licence plate is saved in plateNumber(can be taken with get_lp())
    '''
    def __init__(self, file_name="../saved/plate2.jpeg", enhance=True, visu=False, predictor=None):
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
        self.gray_img = cv2.imread(file_name, 0)                                # read the image
        self.gray_img = imutils.resize(self.gray_img, height=100, width=230)    # resize the image
        if self.visu:
            cv2.imshow("original", self.gray_img)

        self.gray_img = self.pow_law_transformation(self.gray_img)              # enhance

        # create a binary image that has all letters as a connected component
        bin_image = self.mser_processor(self.gray_img)

        # segement the characters from the binary image
        self.segment_chars(bin_image)

        if self.visu:
            cv2.imshow("mesr+otsu_regional", bin_image)
            cv2.waitKey()

        print("detected LP:" + self.plateNumber)

        # track detections result in a txt file
        with open(ROOT_DIR+"\\plates.txt", "a") as myfile:
            myfile.write(file_name + " " + self.plateNumber + "\n")

    def get_lp(self):
        return self.plateNumber

    def pow_law_transformation(self, gray_img_p):
        im_power_law_transformation = gray_img_p / 255.0
        im_power_law_transformation = cv2.pow(im_power_law_transformation, 0.6)
        im_power_law_transformation = img_as_ubyte(im_power_law_transformation)
        if self.visu:
            cv2.imshow("power transfomration", im_power_law_transformation)
        return im_power_law_transformation

    def mser_processor(self, cv_image, debug=False):

        # create an empty np array of the shape of the image
        mask = np.zeros(self.gray_img.shape, dtype=np.uint8)

        # user cv2 MSER to extract regions
        mser = cv2.MSER_create()
        regions, _ = mser.detectRegions(cv_image)

        for p in regions:
            xmax, ymax = np.amax(p, axis=0)
            xmin, ymin = np.amin(p, axis=0)

            # filter the regions
            if abs(ymax - ymin) > 50 or abs(ymax - ymin) < 10 or abs(xmax - xmin) > 30 or abs(xmax - xmin) < 10:
                continue
            if debug:
                print("rectangle (xmin=%02d,ymin=%02d) -> (xmax=%02d,ymax=%02d) " % (xmin, ymin, xmax, ymax))

            # compute the value of the OTSU threshold for a given region(not valid for the whole image)
            val = filters.threshold_otsu(cv_image[ymin:ymax, xmin:xmax])

            # construct a mask for the current rectangle
            slice_of_mask = np.zeros(self.gray_img.shape, dtype=np.uint8)

            # apply otsu threshold
            slice_of_mask[cv_image < val] = 255

            # copy to the to the global mask only the slice for which we applied the threshold
            mask[ymin:ymax, xmin:xmax] = slice_of_mask[ymin:ymax, xmin:xmax]

            # if we don't want to apply the threshold we could simply put the values from the initial image
            # in a specific region to the exact same region in the glabal mask
            # mask[ymin:ymax, xmin:xmax] = cv_image[ymin:ymax, xmin:xmax]

            # draw on vis the rectangle
            # cv2.rectangle(vis, (xmin, ymax), (xmax, ymin), (128, 128, 128), 1)
        return mask

    def segment_chars(self, image):
        ret, labels = cv2.connectedComponents(image)
        try:
            os.mkdir(ROOT_DIR + "\chars\plate" + self.palteNo)
            print("created dir " + ROOT_DIR + "chars\plate" + self.palteNo)
        except:
            pass
        symbols = []
        for crt in range(1, ret):
            oneSymbol = np.where(labels == crt, len(labels), 0)

            first_non_empty_col = MSER_Segmentation.first_nonzero(oneSymbol, axis=0)

            #print("data shape " + str(oneSymbol.shape))
            #print("character " + str(crt) + " has " + str(first_non_empty_col) + " blank rows to the left.")

            # delete empty rows and columns
            data = np.delete(oneSymbol, np.where(~oneSymbol.any(axis=0))[0], axis=1)
            data = data[~np.all(data == 0, axis=1)]

            symbols.append((data, first_non_empty_col))

        # sort the symbols based on the number of empty columns from left to right
        symbols = sorted(symbols, key=lambda x: x[1])

        for crt in range(len(symbols)):
            self.imshow_components(crt, symbols[crt][0], save=True)

        if self.visu:
            self.imshow_components("letters colored",
                                   labels)  # image with letter segmentation, one color for each symbol

    def imshow_components(self, crt, labels, save=False):
        # Map component labels to hue val
        label_hue = np.uint8(179 * labels / np.max(labels))
        blank_ch = 255 * np.ones_like(label_hue)
        labeled_img = cv2.merge([label_hue, blank_ch, blank_ch])

        if labeled_img.shape[0] < 15 and labeled_img.shape[1] < 15 or labeled_img.shape[0] < 20:
            # discard small images that are not symbols for sure, just some failures
            return

        if labeled_img.shape[0] < 50:
            # cvt to BGR for display sequence of symbols, each with one color
            labeled_img = cv2.cvtColor(labeled_img, cv2.COLOR_BGR2GRAY)
        else:
            # cvt to grayscale for display one symbol
            labeled_img = cv2.cvtColor(labeled_img, cv2.COLOR_HSV2BGR)

        # set bg label to black
        labeled_img[label_hue == 0] = 0

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
