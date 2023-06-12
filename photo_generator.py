import PIL
from PIL import Image, ImageFilter
import os
from random import randint
import math
from utils import generate_file_name, substring_after, get_weather_icon_id

MAX_ZOOM = 5

IMAGE_FORMATS = ('.png', '.JPG', 'jpg', '.jpeg', '.JPEG', '.PNG')

PLACE_IMAGES = 'raw_images/places/'
MASK_IMAGES = 'raw_images/masks/'
MASK_FALL_BACK = MASK_IMAGES + 'fallback/'
WEATHER_IMAGES = 'raw_images/weather'

RESULT_PATH = 'generated_photos/'

PIL.Image.MAX_IMAGE_PIXELS = None

def get_all_image_paths(root_path):
    return [os.path.join(root, name)
            for root, dirs, files in os.walk(root_path)
            for name in files if name.endswith(IMAGE_FORMATS) and not name.startswith('.')]


def get_images_for_subdirectories(root_path):
    directory_dict = {}
    iter_dir = iter(os.walk(root_path))
    next(iter_dir)
    for subdirectory in iter_dir:
        name = subdirectory[0]
        head, tail = os.path.split(name)
        directory_dict[tail] = get_all_image_paths(name)
    return directory_dict


def rescale(image, dimensions):
    """Rescale the given image, optionally cropping it to make sure the result image has the specified width and height."""

    max_width = dimensions[0]
    max_height = dimensions[1]

    src_width, src_height = image.size
    src_ratio = float(src_width) / float(src_height)
    dst_width, dst_height = max_width, max_height
    dst_ratio = float(dst_width) / float(dst_height)

    if dst_ratio < src_ratio:
        crop_height = src_height
        crop_width = crop_height * dst_ratio
        x_offset = float(src_width - crop_width) / 2
        y_offset = 0
    else:
        crop_width = src_width
        crop_height = crop_width / dst_ratio
        x_offset = 0
        y_offset = float(src_height - crop_height) / 3
    image = image.crop((x_offset, y_offset, x_offset + int(crop_width), y_offset + int(crop_height)))
    image = image.resize((dst_width, dst_height))

    return image


def zoom_at(img, x, y, zoom):
    w, h = img.size
    zoom2 = zoom * 2
    img = img.crop((x - w / zoom2, y - h / zoom2,
                    x + w / zoom2, y + h / zoom2))
    return img.resize((w, h), Image.LANCZOS)


place_image_paths = get_images_for_subdirectories(PLACE_IMAGES)
weather_image_paths = get_images_for_subdirectories(WEATHER_IMAGES)

mask_image_paths = get_all_image_paths(MASK_FALL_BACK)


def generate_photo(place_name, place_weather_id, camp_progression):
    zoom_level = MAX_ZOOM + 1 - (math.sqrt(camp_progression) * MAX_ZOOM)

    # get the weather id; usually for displaying an icon, we use it to select an appropriate weather photo
    weather_id = get_weather_icon_id(place_weather_id)

    # get path to available photos for the selected place and weather
    current_weather_paths = weather_image_paths[weather_id]
    current_place_paths = place_image_paths[place_name]

    # select photos for the requested place and weather
    place_image_path = current_place_paths[randint(0, len(current_place_paths) - 1)]
    weather_image_path = current_weather_paths[randint(0, len(current_weather_paths) - 1)]

    # get the path for the correct mask
    sub_directories = substring_after(place_image_path, PLACE_IMAGES)
    mask_path = MASK_IMAGES + sub_directories
    without_ending = os.path.splitext(mask_path)[0]
    mask_path = without_ending + '.png'

    if not os.path.isfile(mask_path):
        mask_path = mask_image_paths[randint(0, len(mask_image_paths) - 1)]

    # load the photos
    background = Image.open(weather_image_path)
    foreground = Image.open(place_image_path)
    mask = Image.open(mask_path)

    mask = mask.filter(ImageFilter.GaussianBlur(radius=7))

    # resize the mask (aspect ratio is not important here) and rescale (i.e. crop and zoom if necessary) the weather photo
    mask = mask.resize(foreground.size)
    background = rescale(background, foreground.size)
    foreground = zoom_at(foreground, foreground.size[0] / 2, foreground.size[1] / 2, zoom_level)
    mask = zoom_at(mask, mask.size[0] / 2, mask.size[1] / 2, zoom_level)

    # merge weather and place photo using the mask
    background.paste(foreground, (0, 0), mask)

    file_name = generate_file_name(RESULT_PATH + "place_photo_")
    background.save(file_name)

    return file_name, place_image_path

