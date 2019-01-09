import traceback
from PIL import Image, ExifTags
from keras.models import model_from_json
from keras.preprocessing.image import load_img, img_to_array
import numpy as np
import tensorflow as tf
from scipy.misc import imresize
import os
import path_config
from keras.optimizers import Adam
from keras.models import Model
from keras.layers import Input, Dense, Flatten, Dropout, average
from sklearn.model_selection import train_test_split
from keras.applications.inception_v3 import InceptionV3
from keras.applications.resnet50 import ResNet50
from keras.applications.inception_resnet_v2 import InceptionResNetV2

IMAGE_WIDTH = 224
IMAGE_HEIGHT = 224


def process_raw_image(image):
    return img_to_array(load_img(image, target_size=(224, 224)))


def rotate_by_exif(image):
    try :
        for orientation in ExifTags.TAGS.keys() :
            if ExifTags.TAGS[orientation]=='Orientation' : break
        exif=dict(image._getexif().items())
        if not orientation in exif:
            return image

        if   exif[orientation] == 3 :
            image=image.rotate(180, expand=True)
        elif exif[orientation] == 6 :
            image=image.rotate(270, expand=True)
        elif exif[orientation] == 8 :
            image=image.rotate(90, expand=True)
        return image
    except:
        return image

class Pred_Model_Base(object):
    def __init__(self):
        self.data = None
        self.graph = tf.get_default_graph()
        self.model = None
    
    def load_model(self, json_file, model_weight_file):
#         with open(json_file, encoding='utf-8') as weight_file:
#             self.data = weight_file.read()
        json_file_op = open(json_file, 'r')
        loaded_model_json = json_file_op.read()
        json_file_op.close()
        self.data = loaded_model_json
        self.model = model_from_json(self.data)
        self.model.load_weights(model_weight_file)
        self.model.compile(loss='binary_crossentropy',
                     optimizer=Adam(lr=1e-5, beta_1=0.9, beta_2=0.999, decay=1e-5),
                     metrics=['accuracy'])
        print('load {0}'.format(model_weight_file))

    def load_ensemble_model(self, model_weight_file):
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
        ensemble_model.load_weights(model_weight_file)
        self.model = ensemble_model


    def _ml_predict(self, image):
        prediction = -1
        with self.graph.as_default():
            # Add a dimension for the batch
            if self.model is not None:
                prediction = self.model.predict(image[None, :, :, :])
        return prediction
    
    def predict_image(self, image):
#         image = rotate_by_exif(image) # current rotate function is so stable
        resized_image = imresize(image, (224, 224)) / 255.0
    
        # Model input shape = (224,224,3)
        # [0:3] - Take only the first 3 RGB channels and drop ALPHA 4th channel in case this is a PNG
        try:
            pred = self._ml_predict(resized_image[:, :, 0:3])
            prediction = np.float64(pred.take(0, axis=0)[0])
            return float('%.5f' % prediction)
        except:
            return 0        
    
    def predict(self, image_path, lock_object = None):
        test_images = list()
        test_images.append(process_raw_image(image_path))
        X = np.array(test_images)
        X_norm = X/255
        prediction = -1
        with self.graph.as_default():
            if lock_object is not None:
                with lock_object:
                    prediction = self.model.predict(X_norm, batch_size=1, verbose=1, steps=None)[0][0]
            else:
                prediction = self.model.predict(X_norm, batch_size=1, verbose=1, steps=None)[0][0]
            return float('%.3f' % prediction)      
#         image = Image.open(image_path)
#         return self.predict_image(image)
        

class Alcohol_Model(Pred_Model_Base):
    
    def __init__(self):
        Pred_Model_Base.__init__(self)
        #json_file=path_config.alcohol_json_file
        model_weight_file = path_config.alcohol_h5_file
        #self.load_model(json_file, model_weight_file)
        self.load_ensemble_model(model_weight_file)

class Gambling_Model(Pred_Model_Base):
    
    def __init__(self):
        Pred_Model_Base.__init__(self)
        #json_file=path_config.gambling_json_file
        model_weight_file = path_config.gambling_h5_file
        #self.load_model(json_file, model_weight_file)
        self.load_ensemble_model(model_weight_file)