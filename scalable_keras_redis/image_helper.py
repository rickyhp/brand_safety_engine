from PIL import Image

def check_image_with_pil(path):
    try:
        Image.open(path)
    except IOError:
        return False
    return True