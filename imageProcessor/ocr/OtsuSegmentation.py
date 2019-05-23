import cv2
import imutils
import numpy as np
from skimage import img_as_ubyte


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

def imshow_components2(crt, labels, save=False):
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

    cv2.imshow(str(crt), labeled_img)

    # cv2.imwrite(ROOT_DIR + "\\chars\\plate" + self.palteNo + "\\c" + str(crt) + ".jpeg", labeled_img)

    try:
        crt = int(crt)
        # symbol = predictor.run("\\chars\\plate" + self.palteNo + "\\c" + str(crt) + ".jpeg")
        # plateNumber = plateNumber + symbol
    except ValueError:
        pass

def first_nonzero(arr, axis, invalid_val=-1):
    mask = arr != 0
    non_zero_indexes = np.where(mask.any(axis=axis), mask.argmax(axis=axis), invalid_val)
    mask = non_zero_indexes != -1
    return np.where(mask.any(axis=axis), mask.argmax(axis=axis), 0)

def pow_law_transformation(gray_img_p,gamma):
    im_power_law_transformation = gray_img_p / 255.0
    im_power_law_transformation = cv2.pow(im_power_law_transformation, gamma)
    im_power_law_transformation = img_as_ubyte(im_power_law_transformation)
    return im_power_law_transformation


gamma = 2
plate = cv2.imread("../saved2/plate2.jpeg", 0)
plate = imutils.resize(plate, height=100, width=230)    # resize the image

print(cv2.mean(plate[25:60,90:130]))

cv2.imshow("original", plate)
plate = pow_law_transformation(plate, gamma)
cv2.imshow("pow transofrmed", plate)


# Otsu's thresholding after Gaussian filtering
blur = cv2.GaussianBlur(plate, (5, 5), 0)
ret3, th3 = cv2.threshold(plate, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
cv2.imshow("otsu", th3)

th3 = cv2.bitwise_not(th3)
ret, labels = cv2.connectedComponents(th3)

imshow_components(0, labels)

symbols = []
for crt in range(1, ret):
    oneSymbol = np.where(labels == crt, len(labels), 0)

    first_non_empty_col = first_nonzero(oneSymbol, axis=0)

    # delete empty rows and columns
    data = np.delete(oneSymbol, np.where(~oneSymbol.any(axis=0))[0], axis=1)
    data = data[~np.all(data == 0, axis=1)]

    symbols.append((data, first_non_empty_col))

# sort the symbols based on the number of empty columns from left to right
symbols = sorted(symbols, key=lambda x: x[1])

for crt in range(len(symbols)):
    imshow_components2(crt, symbols[crt][0])
cv2.waitKey()


