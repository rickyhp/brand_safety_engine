import argparse
import glob
import os
import sys
import time
from io import BytesIO
import caffe
import numpy as np
from PIL import Image


def resize_image(data, sz=(256, 256)):
    """
    Resize image. Please use this resize logic for best results instead of the 
    caffe, since it was used to generate training dataset 
    :param byte data:
        The image data
    :param sz tuple:
        The resized image dimensions
    :returns bytearray:
        A byte array with the resized image
    """
    im = Image.open(BytesIO(data))
    if im.mode != "RGB":
        im = im.convert('RGB')
    imr = im.resize(sz, resample=Image.BILINEAR)
    fh_im = BytesIO()
    imr.save(fh_im, format='JPEG')
    fh_im.seek(0)
    return fh_im

class Nude_Model(object):
    def __init__(self):
        self.nsfw_net = caffe.Net('nsfw_model/deploy.prototxt',  # pylint: disable=invalid-name
                    'nsfw_model/resnet_50_1by2_nsfw.caffemodel', caffe.TEST)
        print("Nude_Model caffe model loaded")
        # Load transformer
        # Note that the parameters are hard-coded for best results
        self.caffe_transformer = caffe.io.Transformer({'data': self.nsfw_net.blobs['data'].data.shape})
        self.caffe_transformer.set_transpose('data', (2, 0, 1))  # move image channels to outermost
        self.caffe_transformer.set_mean('data', np.array([104, 117, 123]))  # subtract the dataset-mean value in each channel
        self.caffe_transformer.set_raw_scale('data', 255)  # rescale from [0, 1] to [0, 255]
        self.caffe_transformer.set_channel_swap('data', (2, 1, 0))  # swap channels from RGB to BGR
    
    def predict(self, image_path, lock_object = None):
        image_data = open(image_path, 'rb').read()
        # Classify.
        scores = self.caffe_preprocess_and_compute(image_data, output_layers=['prob'])
        return scores[1]
    
    def caffe_preprocess_and_compute(self, pimg, 
                                 output_layers=None):
        """
        Run a Caffe network on an input image after preprocessing it to prepare
        it for Caffe.
        :param PIL.Image pimg:
            PIL image to be input into Caffe.
        :param caffe.Net caffe_net:
        :param list output_layers:
            A list of the names of the layers from caffe_net whose outputs are to
            to be returned.  If this is None, the default outputs for the network
            are returned.
        :return:
            Returns the requested outputs from the Caffe net.
        """
        if self.nsfw_net is not None:
    
            # Grab the default output names if none were requested specifically.
            if output_layers is None:
                output_layers = self.nsfw_net.outputs
    
            img_bytes = resize_image(pimg, sz=(256, 256))
            image = caffe.io.load_image(img_bytes)
    
            H, W, _ = image.shape
            _, _, h, w = self.nsfw_net.blobs['data'].data.shape
            h_off = max((H - h) / 2, 0)
            w_off = max((W - w) / 2, 0)
            crop = image[int(h_off):int(h_off + h), int(w_off):int(w_off + w), :]
            transformed_image = self.caffe_transformer.preprocess('data', crop)
            transformed_image.shape = (1,) + transformed_image.shape
    
            input_name = self.nsfw_net.inputs[0]
            all_outputs = self.nsfw_net.forward_all(blobs=output_layers,
                                                **{input_name: transformed_image})
    
            outputs = all_outputs[output_layers[0]][0].astype(float)
            return outputs
        else:
            return []
