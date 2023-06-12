import datetime
import os
import time

import pyowm


def generate_file_name(prefix):
    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('_%Y%m%d_%H_%M_%S')
    return prefix + timestamp + ".jpg"


def post_screenshot(bot, chat_id, file_name):
    photo = open(file_name, 'rb')
    bot.send_photo(chat_id, photo)
    os.remove(file_name)


def substring_after(s, delim):
    return s.partition(delim)[2]


def get_weather_icon_id(place_weather_id):
    return get_weather(place_weather_id).get_weather_icon_name()[:-1]


def get_weather(place_weather_id):
    # Weather API Key
    api_key = open('weather_key.txt').read().strip()
    owm = pyowm.OWM(api_key)
    observation = owm.weather_at_id(place_weather_id)
    return observation.get_weather()
