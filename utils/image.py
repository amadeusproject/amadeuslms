import os
import math
from PIL import Image

MAX_IMAGE_SIZE = 1048576 # 1 MB


def image_resize(image_path: str):

    while os.path.getsize(image_path) > MAX_IMAGE_SIZE:
        image = Image.open(image_path)
        width, height = image.size

        new_width = math.floor(width * .9)
        new_height = math.floor(height * .9)

        image = image.resize((new_width, new_height), Image.ANTIALIAS)
        image.save(image_path, quality=100)
        image.close()
