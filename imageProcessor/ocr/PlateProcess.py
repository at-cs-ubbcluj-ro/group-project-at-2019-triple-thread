import os

from PIL import Image
import pytesseract
import cv2
import numpy as np
import scipy.fftpack

from letter_recognition.PredictLP import PredictLP

ROOT_DIR = os.path.split(os.environ['VIRTUAL_ENV'])[0]


class LPP:
    '''
        license plate processing
        input: a cropped image of a license plate from a car
        output: sequence of images characters segmented from the licence plate
    '''

    def __init__(self):
        self.visu = True
        self.plateNumber = ""

    def run(self, file_name="demo2/plate3.jpg", image=None):

        print("processing  plate image")
        if image is None:
            image = cv2.imread(ROOT_DIR + "\\" + file_name, 0)
        IOpen = self.crop_and_filter(image)

        print("segmenting characters of a plate")
        self.segment_chars(IOpen)
        print("The LP of the car in " + file_name + " is:" + self.plateNumber)
        # in the future this number will be sent to a cloud

        if self.visu:
            cv2.waitKey()

    def imclearborder(self, imgBW, radius):
        # Given a black and white image, first find all of its contours
        imgBWcopy = imgBW.copy()
        contours, hierarchy = cv2.findContours(imgBWcopy.copy(), cv2.RETR_LIST,
                                               cv2.CHAIN_APPROX_SIMPLE)

        # Get dimensions of image
        imgRows = imgBW.shape[0]
        imgCols = imgBW.shape[1]

        contourList = []  # ID list of contours that touch the border

        # For each contour...
        for idx in np.arange(len(contours)):
            # Get the i'th contour
            cnt = contours[idx]

            # Look at each point in the contour
            for pt in cnt:
                rowCnt = pt[0][1]
                colCnt = pt[0][0]

                # If this is within the radius of the border
                # this contour goes bye bye!
                check1 = (0 <= rowCnt < radius) or (imgRows - 1 - radius <= rowCnt < imgRows)
                check2 = (0 <= colCnt < radius) or (imgCols - 1 - radius <= colCnt < imgCols)

                if check1 or check2:
                    contourList.append(idx)
                    break

        for idx in contourList:
            cv2.drawContours(imgBWcopy, contours, idx, (0, 0, 0), -1)

        return imgBWcopy

    @staticmethod
    def bw_area_open(imgBW, areaPixels):
        # Given a black and white image, first find all of its contours
        imgBWcopy = imgBW.copy()
        contours, hierarchy = cv2.findContours(imgBWcopy.copy(), cv2.RETR_LIST,
                                               cv2.CHAIN_APPROX_SIMPLE)

        # For each contour, determine its total occupying area
        for idx in np.arange(len(contours)):
            area = cv2.contourArea(contours[idx])
            if 0 <= area <= areaPixels:
                cv2.drawContours(imgBWcopy, contours, idx, (0, 0, 0), -1)

        return imgBWcopy

    def crop_and_filter(self, image):
        # Number of rows and columns
        rows = image.shape[0]
        cols = image.shape[1]

        # Remove some columns from the beginning and end
        #image = image[:, 59:cols - 20]

        # Number of rows and columns
        rows = image.shape[0]
        cols = image.shape[1]

        # Convert image to 0 to 1, then do log(1 + I)
        imgLog = np.log1p(np.array(image, dtype="float") / 255)

        # Create Gaussian mask of sigma = 10
        M = 2 * rows + 1
        N = 2 * cols + 1
        sigma = 10
        (X, Y) = np.meshgrid(np.linspace(0, N - 1, N), np.linspace(0, M - 1, M))
        centerX = np.ceil(N / 2)
        centerY = np.ceil(M / 2)
        gaussianNumerator = (X - centerX) ** 2 + (Y - centerY) ** 2

        # Low pass and high pass filters
        Hlow = np.exp(-gaussianNumerator / (2 * sigma * sigma))
        Hhigh = 1 - Hlow

        # Move origin of filters so that it's at the top left corner to
        # match with the input image
        HlowShift = scipy.fftpack.ifftshift(Hlow.copy())
        HhighShift = scipy.fftpack.ifftshift(Hhigh.copy())

        # Filter the image and crop
        If = scipy.fftpack.fft2(imgLog.copy(), (M, N))
        Ioutlow = scipy.real(scipy.fftpack.ifft2(If.copy() * HlowShift, (M, N)))
        Iouthigh = scipy.real(scipy.fftpack.ifft2(If.copy() * HhighShift, (M, N)))

        # Set scaling factors and add
        gamma1 = 0.3
        gamma2 = 1.5
        Iout = gamma1 * Ioutlow[0:rows, 0:cols] + gamma2 * Iouthigh[0:rows, 0:cols]

        # Anti-log then rescale to [0,1]
        Ihmf = np.expm1(Iout)
        Ihmf = (Ihmf - np.min(Ihmf)) / (np.max(Ihmf) - np.min(Ihmf))
        Ihmf2 = np.array(255 * Ihmf, dtype="uint8")

        # Threshold the image - Anything below intensity 65 gets set to white
        Ithresh = Ihmf2 < 65
        Ithresh = 255 * Ithresh.astype("uint8")

        # Clear off the border.  Choose a border radius of 5 pixels
        Iclear = self.imclearborder(Ithresh, 1)

        # Eliminate regions that have areas below 120 pixels
        Iopen = LPP.bw_area_open(Iclear, 3)

        if self.visu:
            # Show all images

            cv2.imshow('Original Image', image)
            cv2.imshow('Homomorphic Filtered Result', Ihmf2)
            cv2.imshow('Thresholded Result', Ithresh)
            cv2.imshow('Opened Result', Iopen)
            cv2.waitKey()
        return Iopen

    def imshow_components(self, crt, labels, save=False):

        # Map component labels to hue val
        label_hue = np.uint8(179 * labels / np.max(labels))
        blank_ch = 255 * np.ones_like(label_hue)
        labeled_img = cv2.merge([label_hue, blank_ch, blank_ch])

        # cvt to BGR for display
        labeled_img = cv2.cvtColor(labeled_img, cv2.COLOR_BGR2GRAY)

        # set bg label to black
        labeled_img[label_hue == 0] = 0
        if self.visu:
            cv2.imshow(str(crt), labeled_img)

        if save:
            # for now, for the ease of the development process we will save the images
            cv2.imwrite(ROOT_DIR + "\\chars\\c" + str(crt) + ".jpeg", labeled_img)

        try:
            crt = int(crt)
            symbol = self.predictor.run("\\chars\\c" + str(crt) + ".jpeg")
            self.plateNumber = self.plateNumber + symbol
        except ValueError:
            pass

    def segment_chars(self, image):

        ret, labels = cv2.connectedComponents(image)

        self.predictor = PredictLP()
        for crt in range(1, ret):
            oneSymbol = np.where(labels == crt, len(labels), 0)

            data = np.delete(oneSymbol, np.where(~oneSymbol.any(axis=0))[0], axis=1)
            data = data[~np.all(data == 0, axis=1)]
            self.imshow_components(crt, data, save=True)

            # print("symbol" + str(crt) + " is " + str(pytesseract.image_to_string(oneSymbol)))
        if self.visu:
            self.imshow_components("letters colored",
                                   labels)  # image with letter segmentation, one color for each symbol
            # cv2.imshow("Iopen", image)  # image with filters applied
