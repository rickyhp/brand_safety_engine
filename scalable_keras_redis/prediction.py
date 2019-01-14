from classifiers import Alcohol_Model, Gambling_Model
from classify_nsfw import Nude_Model
import mongodb_helper
from mongodb_helper import Mongodb_helper
from pymongo import MongoClient
import image_helper
from threading import Thread, Lock
import queue
from numpy import double
import settings

model = Alcohol_Model()
gm_model = Gambling_Model()
nude_model = Nude_Model()
lock_object = Lock()

def Generate_Record(website_folder, url, image_name, result, suspicous):
    return {settings.Website_Folder_Column : website_folder,
            settings.Website_Column : url, 
            settings.Image_Name_Column : image_name,
            settings.Result_Column : result,
            settings.Suspicious_Column : suspicous}

class Prediction(object):
    def __init__(self, url, image_path, image_name, website_folder, is_slices):
        self.image_path = image_path
        self.image_name = "/static/{0}/{1}".format(website_folder, 'slices/'+image_name if is_slices else image_name)
        self.website_folder = website_folder
        self.url = url
        self.alcohol = model
        self.gambling = gm_model
        self.nudity = nude_model
        self.is_slices = is_slices
        self.mongo_helper = Mongodb_helper()
        self.results = {}
    
    def _thread_func(self, func, image_path, out_queue, label, lock_object):
        score = func(image_path, lock_object)
        out_queue.put({label : score})
        
    def predict(self):
        if image_helper.check_image_with_pil(self.image_path):
#             alcohol_score = self.alcohol.predict(self.image_path)
#             gambling_score = self.gambling.predict(self.image_path)
            out_queue = queue.Queue()
            threads = []
            for x in settings.Categories_In_Program:
                if x == settings.Category_Alcohol:
                    threads.append(Thread(target=self._thread_func, args = (self.alcohol.predict, self.image_path, out_queue, settings.Category_Alcohol, lock_object)))
                if x == settings.Category_Gambling:
                    threads.append(Thread(target=self._thread_func, args = (self.gambling.predict, self.image_path, out_queue, settings.Category_Gambling, lock_object)))
                if x == settings.Category_Nudity:
                    threads.append(Thread(target=self._thread_func, args = (self.nudity.predict, self.image_path, out_queue, settings.Category_Nudity, lock_object)))
            # put nudity thread here
            for t in threads:
                t.start()
            for th in threads:
                th.join()
#             t2 = 
#             t1.start()
#             t2.start()
#             t1.join()
#             t2.join()
            dict = settings.default_result()
#             dict = {'alcohol' : alcohol_score, 'gambling' : gambling_score}
            max_pred = 0
#             max_pred = max(alcohol_score, gambling_score)
            need_to_insert = False
            for q in range(out_queue.qsize()):
                for key, value in out_queue.get().items():
                    dict[key] = value                    
                    if max_pred <= value:
                        max_pred = value
            suspicious = max_pred >= settings.stoping_threshold
            record = Generate_Record(self.website_folder, self.url, self.image_name, dict, suspicious)
            self.mongo_helper.Insert_Record(record)
            print('{0} predicted : {1}'.format(self.image_path, str(max_pred)))
            return max_pred
        return -1;