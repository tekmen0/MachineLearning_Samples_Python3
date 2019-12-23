import matplotlib
#this is to save plot to the disk
#usually used while using cloud servers
matplotlib.use("Agg")

from keras.preprocessing.image import ImageDataGenerator
from keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from keras.preprocessing.image import img_to_array
from keras.utils import to_categorical
from build_model import LeNet
from imutils import paths #bunu opencv ve matplotlible kendim de yapabilirim

import matplotlib.pyplot as plt
import numpy as np
import argparse
import random
import cv2
import os

ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dataset", required=True,
                help = "path to input dataset folder")
ap.add_argument("-m", "--model", default=os.path.curdir,
                help = "path to output model")
ap.add_argument("-p", "--plot", type=str, default="plot.png",
                help="path to output accuracy/loss plot")
args = vars(ap.parse_args())

print("type: ", type(args), "args : ", args)

# initialize the number of epochs to train for, initial learning rate,
# and batch size

EPOCHS = 25 #? what is epoch
INIT_LR = 1e-3 #? why it is represented with e
BS = 32 #?

# initialize the data and labels
print("[INFO] loading images...")
data = []
labels = []

#grab the image paths and randomly shuffle them
imagePaths = sorted(list(paths.list_images(args["dataset"]))) #list of image paths

# loop over the input images
for imagePath in imagePaths:
    # load the image, pre-process it, and store it in the data list
    image = cv2.imread(imagePath)
    image = cv2.resize(image, (28,28))
    image = img_to_array(image) # turns int-8's to float32's
    data.append(image)

    # extract the class label from the image path and update the
    # labels list
    label = imagePath.split(os.path.sep)[-2]
    label = 1 if label == "looking" else 0
    labels.append(label)

# scale the raw pixel intesities to the range [0,1]
data = np.array(data, dtype="float")/255.0
labels = np.array(labels)

# partition the data into training and testing splits using %75 of
# the data for training and rest for the testing
(trainX, testX, trainY, testY) = train_test_split(data,
    labels, test_size=0.25, random_state=42)

# convert the labels from integers to vectors
trainY = to_categorical(trainY, num_classes=2) #?
testY = to_categorical(testY, num_classes=2) #integer to floating point-32

# construct the image generator for data augmentation
aug = ImageDataGenerator(rotation_range=30, width_shift_range=0.1,
                height_shift_range=0.1, shear_range=0.2, zoom_range=0.2,
                horizontal_flip=True, fill_mode="nearest")

# initialize the model
# some other models rather than LeNet: ResNet, GoogLeNet, SqueezeNet
print("[INFO], compiling model...")
model = LeNet.build(width=28, height=28, depth=3, classes=2)
opt = Adam(lr=INIT_LR, decay=INIT_LR / EPOCHS) #?
model.compile(loss="binary_crossentropy", optimizer=opt,
	metrics=["accuracy"])

# train the network
print("[INFO] training network...")
H = model.fit_generator(aug.flow(trainX, trainY, batch_size=BS),
	validation_data=(testX, testY), steps_per_epoch=len(trainX) // BS,
	epochs=EPOCHS, verbose=1)

# save the model to disk
print("[INFO] serializing network...")
model.save(args["model"])






