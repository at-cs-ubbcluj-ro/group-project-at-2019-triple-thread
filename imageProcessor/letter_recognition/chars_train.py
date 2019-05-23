from keras.datasets import mnist
from keras.engine.saving import load_model
from keras.models import Sequential
from keras.layers import Dense, Input, merge
from keras.layers import Dropout
from keras.layers import Flatten
from keras.utils import np_utils
from keras.optimizers import SGD, adadelta
from keras.layers import Dense, Dropout, Flatten, Activation, Convolution2D, MaxPooling2D, BatchNormalization, \
    AveragePooling2D
import os, glob
import numpy as np
import csv
import pandas as pd
import cv2 as cv
from sklearn.utils import shuffle
from keras.callbacks import EarlyStopping, ModelCheckpoint
from keras import callbacks, losses
import matplotlib.pyplot as plt
import numpy

seed = 7
np.random.seed(seed)

# path to training images
path = 'English/Img/GoodImg/Bmp/'
#path = 'segmented/'
img_rows, img_cols, img_channels = [40, 40, 1]
nb_classes = 36

# defining convolution layer and max pooling layer window size
nb_conv = 3
nb_pool = 2


def load_data(dirs, img_rows, img_cols, img_channels):
    """
        Loads all images and their corresponding labels in two python lists.
        Args:
            dirs (list): list of directories containing images of all 62 classes
            img_rows (int): height of images
            img_cols (int): width of images
            img_channels (int): 1 for loading grayscale and 3 for loading color images.
        Returns:
            list: two lists containign images and their labels.
    """
    X = []
    y = []
    label = 0
    print('loading images .. ')
    for d in dirs:
        dir_path = os.path.join(path, d)
        image_list = os.listdir(dir_path)
        for im in image_list:
            img_path = os.path.join(dir_path, im)
            if img_channels == 1:
                img = cv.imread(img_path, 0)
            else:
                img = cv.imread(img_path)
            img = cv.resize(img, (img_rows, img_cols))
            X.append(img)
            y.append(label)
        label = label + 1
    print('Complete!')
    return X, y


def prepare_data_for_training(X, y, img_rows, img_cols, img_channels):
    """
        Properly formats the loaded data for training
        Args:
            X (list): list of images
            y (list): list containing image labels
            img_rows (int): height of images
            img_cols (int): width of images
            img_channels (int): 1 for loading grayscale and 3 for loading color images.
        Returns:
            list: two properly formatted lists
    """

    X = np.asarray(X, dtype='float32')
    y = np.asarray(y)
    if img_channels == 1:
        X = X.reshape(X.shape[0], img_channels, img_rows, img_cols)
    else:
        X = np.transpose((0, 3, 1, 2))

    X, y = shuffle(X, y, random_state=7)  # randomly shuffles the data

    y = np_utils.to_categorical(y, nb_classes)  # converts integer labels to one-hot vector
    return X, y


dirs = sorted(os.listdir(path))

X, y = load_data(dirs, img_rows, img_cols, img_channels)

X, y = prepare_data_for_training(X, y, img_rows, img_cols, img_channels=1)


def create_model():
    """
        Creates a conv-net model
    """
    print("Creating model...")
    model = Sequential()
    model.add(BatchNormalization(input_shape=(img_channels, img_rows, img_cols)))

    model.add(Convolution2D(32, nb_conv, nb_conv, border_mode='same', subsample=(2, 2), init='he_normal'))
    model.add(Activation('relu'))
    model.add(BatchNormalization())

    model.add(Convolution2D(32, nb_conv, nb_conv, border_mode='same', init='he_normal'))
    model.add(Activation('relu'))
    model.add(BatchNormalization())

    model.add(MaxPooling2D(pool_size=(nb_pool, nb_pool), strides=(1, 1), dim_ordering="th"))

    model.add(Convolution2D(48, nb_conv, nb_conv, border_mode='same', subsample=(2, 2), init='he_normal'))
    model.add(Activation('relu'))
    model.add(BatchNormalization())

    model.add(Convolution2D(48, nb_conv, nb_conv, border_mode='same', init='he_normal'))
    model.add(Activation('relu'))
    model.add(BatchNormalization())

    model.add(MaxPooling2D(pool_size=(nb_pool, nb_pool), strides=(1, 1), dim_ordering="th"))

    model.add(Flatten())

    model.add(Dense(256, init='he_normal'))
    model.add(BatchNormalization())
    model.add(Activation('relu'))

    model.add(Dropout(0.5))

    model.add(Dense(nb_classes))
    model.add(Activation('softmax'))

    sgd = SGD(lr=0.01, momentum=0.9, decay=1e-7, nesterov=True)

    model.compile(loss=losses.categorical_hinge, optimizer=sgd, metrics=['accuracy'])
    #'categorical_crossentropy'
    print("Done.")
    return model


model = create_model()

file_path = "weights2.best.hdf5"

# remote = callbacks.RemoteMonitor(root='http://localhost:9000')
checkpoint = ModelCheckpoint(file_path, monitor='val_acc', verbose=1, save_best_only=True, mode='max')

history = model.fit(X, y, callbacks=[checkpoint], validation_split=0.20, nb_epoch=500, shuffle=True, batch_size=32, verbose=1)

# list all data in history
print(history.history.keys())
# summarize history for accuracy
plt.plot(history.history['acc'])
plt.plot(history.history['val_acc'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()
# summarize history for loss
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()
# saving the model
json_string = model.to_json()
f = open('char47k_40x40.json', 'w')
f.write(json_string)
f.close()
