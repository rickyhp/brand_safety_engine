# -*- coding: utf-8 -*-
"""
Created on Wed Dec 26 10:16:27 2018

@author: alphaX
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'

import pickle
from keras.models import model_from_json
from keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from utilities import show_plot
import numpy as np
from sklearn.metrics import confusion_matrix
from keras.applications.inception_v3 import InceptionV3
from keras.applications.resnet50 import ResNet50
from keras.applications.inception_resnet_v2 import InceptionResNetV2
from keras.models import Model
from keras.layers import Input, Dense, Flatten, Dropout, average

import tensorflow as tf
sess = tf.Session(config=tf.ConfigProto(log_device_placement=True))

from keras import backend as K
K.tensorflow_backend._get_available_gpus()

with open("dataset/gambling_images_3.pickle", "rb") as handle:
    X, y = pickle.load(handle)
print("Training data loaded")
    
X_train, X_dev, y_train, y_dev = train_test_split(X, y, test_size=0.2, random_state=88, stratify=y)

#normalize the data
X_train_norm = X_train / 255
X_dev_norm = X_dev / 255
print("Training data split and normalised")

# load test data
data = os.path.join('.', os.path.join('dataset', 'gambling_images_1-005.pickle'))
with open(data, "rb") as handle:
    t_X, t_y = pickle.load(handle)
tX_norm = t_X / 255

print("Testing data loaded and normalised")

#model_filename = os.path.join('.', os.path.join('models_gambling', 'gambling_ensemble_cnn'))
#json_file = open(model_filename+'.json', 'r')
#loaded_model_json = json_file.read()
#json_file.close()
#loaded_model = model_from_json(loaded_model_json)
input_shape = [224,224,3]

inceptionV3_arch = InceptionV3(include_top=False, weights=None, pooling='avg')
in_layer = Input(shape=input_shape, name='image_input')
x = inceptionV3_arch(in_layer)
prediction = Dense(1, activation='sigmoid')(x)
inceptionV3 = Model(inputs=in_layer, outputs=prediction)

resnet50_arch = ResNet50(include_top=False, weights=None, pooling='avg')
in_layer = Input(shape=input_shape, name='image_input')
x = resnet50_arch(in_layer)
prediction = Dense(1, activation='sigmoid')(x)
resnet50 = Model(inputs=in_layer, outputs=prediction)

inceptionResNet_arch = InceptionResNetV2(include_top=False, weights=None, pooling='avg')
in_layer = Input(shape=input_shape, name='image_input')
x = inceptionResNet_arch(in_layer)
prediction = Dense(1, activation='sigmoid')(x)
inceptionResNet = Model(inputs=in_layer, outputs=prediction)

inceptionV3.name = 'InceptionV3'
resnet50.name = 'ResNet50'
inceptionResNet.name = 'InceptionResNetV2'

in_layer = Input(shape=input_shape, name='image_input')
out_inceptionV3 = inceptionV3(in_layer)
out_resnet50 = resnet50(in_layer)
out_inceptionResNet = inceptionResNet(in_layer)
out_models = [out_inceptionV3, out_resnet50, out_inceptionResNet]
prediction = average(out_models)
ensemble_model = Model(inputs=in_layer, outputs=prediction, name='ensemble')
ensemble_model.summary()

filename = "models_gambling/gambling_ensemble_cnn"
ensemble_model.load_weights(filename+'.h5')

loaded_model = ensemble_model
# load weights into new model
#loaded_model.load_weights(model_filename+'.h5')

# evaluate loaded model on test data
loaded_model.compile(loss='binary_crossentropy',
                     optimizer=Adam(lr=1e-5, beta_1=0.9, beta_2=0.999, decay=1e-5),
                     metrics=['accuracy'])

print("Loaded model from disk")

for layer in loaded_model.layers:
    print("%s %s" % (layer.trainable, layer))

batch_size = 6
total_epoch = 4
each_epoch = 1
finish_epoch = 0

history = {'acc':list(), 'val_acc':list(), 'loss':list(), 'val_loss':list()}
for i in range(int(total_epoch/each_epoch)):
    training = loaded_model.fit(X_train_norm, y_train, validation_data=(X_dev_norm, y_dev), epochs=each_epoch, batch_size=batch_size, verbose=1)
    history['acc'].extend(training.history['acc'])
    history['val_acc'].extend(training.history['val_acc'])
    history['loss'].extend(training.history['loss'])
    history['val_loss'].extend(training.history['val_loss'])
    
    score = loaded_model.evaluate(tX_norm, t_y, verbose=0)
    predict = loaded_model.predict(tX_norm, batch_size=1, verbose=1, steps=None)
    predict_class = np.where(predict > 0.5, 1, 0)
    print(confusion_matrix(t_y, predict_class).ravel())
    print(round(score[0], 4))
    print(round(score[1], 4))
    
    filename = "alcohol_ensemble_cnn_retain_v"+str(i+1)
    model_json = loaded_model.to_json()
    with open(filename+".json", "w") as json_file:
        json_file.write(model_json)
    # serialize weights to HDF5
    loaded_model.save_weights(filename+".h5")
    

show_plot(history)






