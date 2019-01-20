
from PIL import Image
import logging
import os
from directory_utils import Folder_Utils
from threading import Thread,  current_thread
from prediction import Prediction
import settings

def check_image_with_pil(path):
    try:
        Image.open(path)
    except IOError:
        return False
    return True

def slice_image(url, website, dest_folder, image_file, height, width, step, lock, terminate):
    dir_helper = Folder_Utils()
    dir_helper.createEmptyFolder(dest_folder)
    im = Image.open(image_file)
    imgwidth, imgheight = im.size;
    count1 = [0]
    count2 = [0]
    if height > imgheight or width > imgwidth:
        try:
            im.save(os.path.join(dest_folder, "sliced.png"))
        except Exception as e:
            print("slicing error : " + e.__str__())
            logging.exception(e.__str__())
        finally:
            return
    x_stop = imgwidth - width
    print('slicing')
    y_stop = imgheight - height
    half_y_stop = int(round(y_stop / 2))
#     yes = crop_image(im, url, website, count1, dest_folder, width, height, x_stop, half_y_stop, step, lock, terminate, 0)
#     if yes:
#         yes = crop_image(im, url, website, count2, dest_folder, width, height, x_stop, y_stop, step, lock, terminate, half_y_stop)
#     
    count = [0]
    crop_image(im, url, website, count, dest_folder, width, height, x_stop, y_stop, step, lock, terminate, 0)
#     t1 = Thread(name="t1", target=crop_image, args=(im, url, website, count1, dest_folder, width, height, x_stop, half_y_stop, step, lock, terminate, 0))
#     t2 = Thread(name="t2", target=crop_image, args=(im, url, website, count2, dest_folder, width, height, x_stop, y_stop, step, lock, terminate, half_y_stop))
#     t1.start()
#     t2.start()
#     t1.join()
#     t2.join()

    
#     print('slicing finished, total {0}'.format(count1[0] + count2[0]))
    
def _crop_image_helper(im, url, website, box, dest_folder, count, name = "0"):
    try:
        count_value = count[0]     
        a = im.crop(box)
        count_value =count_value + 1
        file_name = "sliced-IMG-{0}-{1}.png".format(name, count_value)
        file_path = os.path.join(dest_folder, file_name)          
        a.save(file_path)
        predict = Prediction(url, file_path, file_name, website, True)
        count[0] = count_value
        if predict.predict() >= settings.stoping_threshold or count_value >= 50:
            return False
        return True
    except Exception as e:
        logging.exception(e.__str__())
        return True
    
def crop_image(im, url, website, count, dest_folder, target_width, target_height, x_stop, y_stop, step, lock, terminate, start_y = 0):
    for j in range(start_y, y_stop, step):
        for i in range(0, x_stop, step):        
            box = (i, j, target_width+i, target_height+j)
            if lock is not None:
                with lock:
                    if not terminate: 
                        if _crop_image_helper(im, url, website, box, dest_folder, count, current_thread().getName()) == False:
                            terminate = True
                            print('should stop croping...')
                            return False       
            else:
                if _crop_image_helper(im, url, website, box, dest_folder, count) == False:
                    terminate = True
                    return False
    return True
# slice_image("test", "etcanada.com/news/299494/canadian-tennis-star-eugenie-bouchard-goes-topless-in-sports-illustrated-swimsuit-2018-issue/26.png", 100, 100, 50)  