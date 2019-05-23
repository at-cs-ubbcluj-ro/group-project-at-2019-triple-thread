# load the image and compute the ratio of the old height
# to the new height, clone it, and resize it
import os

import cv2
import imutils as imutils
import numpy as np
from skimage import img_as_ubyte, filters

from letter_recognition.PredictLP import PredictLP

ROOT_DIR = os.path.split(os.environ['VIRTUAL_ENV'])[0]

'''
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


image = cv2.imread("../saved/plate1.jpeg")
ratio = image.shape[0] / 500.0
orig = image.copy()
image = imutils.resize(image, height=100)

# convert the image to grayscale, blur it, and find edges
# in the image
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (7, 7), 0)
edged = cv2.Canny(gray, 75, 200)

# show the original image and the edge detected image
print("STEP 1: Edge Detection")
cv2.imshow("Image", image)
cv2.imshow("Edged", edged)

'''


def mser(cv_image):
    mask = np.zeros(gray_img.shape, dtype=np.uint8)
    # vis = cv_image.copy()
    mser = cv2.MSER_create()
    regions, _ = mser.detectRegions(cv_image)
    for p in regions:
        xmax, ymax = np.amax(p, axis=0)
        xmin, ymin = np.amin(p, axis=0)
        if abs(ymax - ymin) > 50 or abs(ymax - ymin) < 10 or abs(xmax - xmin) > 30 or abs(xmax - xmin) < 10:
            continue
        print("rectangle (xmin=%02d,ymin=%02d) -> (xmax=%02d,ymax=%02d) " % (xmin, ymin, xmax, ymax))

        # compute the value of the OTSU threshold for a given region(not valid for the whole image)
        val = filters.threshold_otsu(cv_image[ymin:ymax, xmin:xmax])

        # construct a mask for the current rectangle
        slice_of_mask = np.zeros(gray_img.shape, dtype=np.uint8)

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


gray_img = cv2.imread("../saved/plate2.jpeg", 0)
gray_img = imutils.resize(gray_img, height=100)
cv2.imshow("original", gray_img)

im_power_law_transformation = gray_img / 255.0
im_power_law_transformation = cv2.pow(im_power_law_transformation, 2)

im_power_law_transformation = img_as_ubyte(im_power_law_transformation)
cv2.imshow("power transfomration", im_power_law_transformation)

gray_img = im_power_law_transformation

mask = mser(gray_img)
cv2.imshow("mesr+otsu_regional", mask)

visu = True
plateNumber = ""


def imshow_components(crt, labels, save=False, plateNumber=""):
    # Map component labels to hue val
    label_hue = np.uint8(179 * labels / np.max(labels))
    blank_ch = 255 * np.ones_like(label_hue)
    labeled_img = cv2.merge([label_hue, blank_ch, blank_ch])

    if labeled_img.shape[0] < 50:
        # cvt to BGR for display sequence of symbols, each with one color
        labeled_img = cv2.cvtColor(labeled_img, cv2.COLOR_BGR2GRAY)
    else:
        # cvt to grayscale for display one symbol
        labeled_img = cv2.cvtColor(labeled_img, cv2.COLOR_HSV2BGR)

    # set bg label to black
    labeled_img[label_hue == 0] = 0
    if visu:
        cv2.imshow(str(crt), labeled_img)

    if save:
        if labeled_img.shape[0] < 15 or labeled_img.shape[1] < 20:
            # discard small images that are not symbols for sure, just some failures
            return

        cv2.imwrite(ROOT_DIR + "\\chars\\c" + str(crt) + ".jpeg", labeled_img)

    try:
        crt = int(crt)
        # symbol = predictor.run("\\chars\\c" + str(crt) + ".jpeg")
        # plateNumber = plateNumber + symbol
    except ValueError:
        pass


def segment_chars(image):
    ret, labels = cv2.connectedComponents(image)

    for crt in range(1, ret):
        oneSymbol = np.where(labels == crt, len(labels), 0)

        # delete empty rows and coloumns
        data = np.delete(oneSymbol, np.where(~oneSymbol.any(axis=0))[0], axis=1)
        data = data[~np.all(data == 0, axis=1)]

        imshow_components(crt, data, save=True)

    if visu:
        imshow_components("letters colored",
                          labels)  # image with letter segmentation, one color for each symbol
        # cv2.imshow("Iopen", image)  # image with filters applied


segment_chars(mask)
cv2.waitKey()
