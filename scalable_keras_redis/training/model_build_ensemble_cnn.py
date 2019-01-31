# -*- coding: utf-8 -*-
"""
Created on Tue Jan  8 22:28:23 2019

@author: alfredt
"""

import pickle
from keras.models import Model
from keras.layers import Input, Dense, Flatten, Dropout, average
from keras.optimizers import Adam
from sklearn.model_selection import train_test_split
import numpy as np
from keras.applications.inception_v3 import InceptionV3
from keras.applications.resnet50 import ResNet50
from keras.applications.inception_resnet_v2 import InceptionResNetV2

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
