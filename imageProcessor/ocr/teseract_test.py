try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract

import cv2
import numpy as np
import scipy.fftpack


def imclearborder(imgBW, radius):
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


def bwareaopen(imgBW, areaPixels):
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


img = cv2.imread('../plate3.jpg', 0)

# Number of rows and columns
rows = img.shape[0]
cols = img.shape[1]

# Remove some columns from the beginning and end
img = img[:, 59:cols - 20]

# Number of rows and columns
rows = img.shape[0]
cols = img.shape[1]

# Convert image to 0 to 1, then do log(1 + I)
imgLog = np.log1p(np.array(img, dtype="float") / 255)

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
Iclear = imclearborder(Ithresh, 5)

# Eliminate regions that have areas below 120 pixels
Iopen = bwareaopen(Iclear, 20)

# Show all images


cv2.imshow('Original Image', img)
cv2.imshow('Homomorphic Filtered Result', Ihmf2)
cv2.imshow('Thresholded Result', Ithresh)
cv2.imshow('Opened Result', Iopen)
cv2.waitKey(0)
cv2.destroyAllWindows()


ret, labels = cv2.connectedComponents(Iopen)


def imshow_components(crt, labels):
    # Map component labels to hue val
    label_hue = np.uint8(179 * labels / np.max(labels))
    blank_ch = 255 * np.ones_like(label_hue)
    labeled_img = cv2.merge([label_hue, blank_ch, blank_ch])

    # cvt to BGR for display
    labeled_img = cv2.cvtColor(labeled_img, cv2.COLOR_BGR2GRAY)

    # set bg label to black
    labeled_img[label_hue == 0] = 0
    cv2.imshow(str(crt), labeled_img)
    cv2.imwrite("C:\\Users\\Stefan-PC\\Documents\\ubb\\anul III\\semestrul II\\AT\\imageServer\\chars\\c" + str(
        crt) + ".jpeg", labeled_img)


for crt in range(1, ret):
    oneSymbol = np.where(labels == crt, len(labels), 0)

    data = np.delete(oneSymbol, np.where(~oneSymbol.any(axis=0))[0], axis=1)
    data = data[~np.all(data == 0, axis=1)]
    imshow_components(crt, data)
    # print("symbol" + str(crt) + " is " + str(pytesseract.image_to_string(oneSymbol)))
imshow_components(crt, labels)
cv2.imshow("Iopen", Iopen)

cv2.waitKey()
# print(pytesseract.image_to_string())
