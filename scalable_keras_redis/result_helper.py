from json import JSONEncoder
from tensorflow.contrib.timeseries.examples import predict

class Prediction_Result(JSONEncoder):
    def __init__(self, image_id = '', predict_label = '', predict_score = 0.0):
        self.image_id = image_id
        self.predict_label = predict_label
        self.predict_score = predict_score
    
    def default(self, o):
        return o.__dict__
    
    def update_image_id(self, image_id):
        self.image_id = image_id
    
    def update_predict_label(self, predict_label):
        self.predict_label = predict_label
    
    def update_predict_score(self, predict_score):
        self.predict_score = predict_score
    
    def keep_best_predict_score(self, predict_score, image_id):
        if self.predict_score < predict_score:
            self.predict_score = predict_score
            self.update_image_id(image_id)