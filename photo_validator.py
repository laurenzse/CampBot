import os
from camp_data import get_session
from camp_data_declarative import LicenseInformation
from PIL import Image
import PIL
import tqdm
from utils import substring_after

PLACE_IMAGES = 'raw_images/places/'
IMAGE_FORMATS = ('.png', '.JPG', 'jpg', '.jpeg', '.JPEG', '.PNG')

PIL.Image.MAX_IMAGE_PIXELS = None

def get_all_image_paths(root_path):
    return [os.path.join(root, name)
            for root, dirs, files in os.walk(root_path)
            for name in files if name.endswith(IMAGE_FORMATS) and not name.startswith(".")]

