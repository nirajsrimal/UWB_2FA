#########################################################################################################
# Credits: The model definition was picked from Kaggle, https://www.kaggle.com/smeschke/four-shapes
# If time permits, we'll train this model with a dataset randomly generated.
# This was used for exploration in using machine learning for pattern detection
#########################################################################################################


import cv2, numpy as np, os

from tensorflow import keras
from tensorflow.keras import layers

from tensorflow.keras.utils import to_categorical

# parameters
img_size = 60  # size of image fed into model


def flatten(dimData, images):
    images = np.array(images)
    images = images.reshape(len(images), dimData)
    images = images.astype('float32')
    images /= 255
    return images


# -------------get train/test data-----------------
# get data
folders, labels, images = ['triangle', 'rectangle', 'circle'], [], []
for folder in folders:
    print(folder)
    for path in os.listdir(os.path.join(os.getcwd(), "gen", folder)):
        img = cv2.imread(os.path.join(os.getcwd(), "gen", folder, path), 0)
        images.append(cv2.resize(img, (img_size, img_size)))
        labels.append(folders.index(folder))

# break data into training and test sets
to_train = 0
train_images, test_images, train_labels, test_labels = [], [], [], []
for image, label in zip(images, labels):
    if to_train < 5:
        train_images.append(image)
        train_labels.append(label)
        to_train += 1
    else:
        test_images.append(image)
        test_labels.append(label)
        to_train = 0

# -----------------keras time --> make the model


# flatten data
dataDim = np.prod(images[0].shape)
# train_data = flatten(dataDim, train_images)
# test_data = flatten(dataDim, test_images)

# change labels to categorical
train_labels = np.array(train_labels)
test_labels = np.array(test_labels)
train_labels_one_hot = to_categorical(train_labels)
test_labels_one_hot = to_categorical(test_labels)

# determine the number of classes
classes = np.unique(train_labels)
nClasses = len(classes)

# three layers
# activation function: both
# neurons: 256
model = keras.Sequential(
    [
        keras.Input(shape=(60, 60, 1)),
        layers.Conv2D(32, kernel_size=(3, 3), activation="relu"),
        layers.MaxPooling2D(pool_size=(2, 2)),
        layers.Conv2D(64, kernel_size=(3, 3), activation="relu"),
        layers.MaxPooling2D(pool_size=(2, 2)),
        layers.Flatten(),
        layers.Dropout(0.5),
        layers.Dense(3, activation="softmax"),
    ]
)


train_images_np = np.array(train_images, dtype=np.uint8)
test_images_np = np.array(test_images, dtype=np.uint8)

model.compile(optimizer='rmsprop', loss='categorical_crossentropy', metrics=['accuracy'])
history = model.fit(train_images_np, train_labels_one_hot, batch_size=256, epochs=50, verbose=1,
                    validation_data=(test_images_np, test_labels_one_hot))

# test model
[test_loss, test_acc] = model.evaluate(test_images_np, test_labels_one_hot)
print("Evaluation result on Test Data : Loss = {}, accuracy = {}".format(test_loss, test_acc))
# save model
model.save('model.h5')
