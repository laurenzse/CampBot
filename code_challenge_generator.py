from camp_data import get_session
from camp_data_declarative import Participant, LicenseInformation, Murderer
from photo_generator import generate_photo
from screenshot_generator import create_instagram_screenshot
from utils import substring_after, get_weather
import os
import random
import locale
import calendar
from datetime import datetime, date
import math

PLACE_IMAGES = 'raw_images/places/'

INSTAGRAM_USER_ID = 'SC19HPINewsBot'
INSTAGRAM_USER_NAME = 'Henriette Peter'

def generate_challenge(participant_id, camp_progression):
    session = get_session()

    participant = session.query(Participant).get(participant_id)

    license_information, photo_file_name = generate_photo_for_participant(camp_progression, participant, session)

    follow_text = get_follow_text(participant)

    date_text = get_date_text(participant)

    like_amount = get_like_amount(participant)

    can_share = get_share_decision(participant)

    can_comment = get_comment_decision(participant)

    heart = get_heart_decision(participant)

    challenge_image = create_instagram_screenshot(INSTAGRAM_USER_ID,
                                                  INSTAGRAM_USER_NAME,
                                                  follow_text,
                                                  photo_file_name,
                                                  heart,
                                                  can_share,
                                                  can_comment,
                                                  like_amount,
                                                  date_text,
                                                  license_information.license,
                                                  license_information.author,
                                                  "(modified) " + license_information.source)

    os.remove(photo_file_name)

    session.close()

    return challenge_image


def generate_photo_for_participant(camp_progression, participant, session):
    participant_partners = get_participant_partners(session, participant)
    participant_partner = random.choice(participant_partners)

    place = participant_partner.city
    weather_id = int(participant_partner.weather_id)

    photo_file_name, place_image_path = generate_photo(place, weather_id, camp_progression)
    place_image_path = substring_after(place_image_path, PLACE_IMAGES)

    license_information = session.query(LicenseInformation).get(place_image_path)

    return license_information, photo_file_name


def get_participant_partners(session, participant):
    participant_partners = []
    this_id = participant.id

    prev_participant = session.query(Participant).order_by(Participant.id.desc()).filter(Participant.id < this_id, Participant.telegram_id.isnot(None)).first()
    if prev_participant is not None:
        participant_partners.append(prev_participant)

    next_participant = session.query(Participant).order_by(Participant.id.asc()).filter(Participant.id > this_id, Participant.telegram_id.isnot(None)).first()
    if next_participant is not None:
        participant_partners.append(next_participant)

    # if we did not find a partner at all, just return original participant (this happens if no one has registered so far --> no telegram_id)
    if not participant_partners:
        participant_partners.append(participant)

    return participant_partners


def get_follow_text(participant):
    if participant.school_year == 10:
        return "Folgen"
    elif participant.school_year == 11:
        return "Abonnieren"
    else:
        return "Follow"


def get_date_text(participant):
    locale.setlocale(locale.LC_ALL, 'de_DE')
    now = datetime.now()

    month = calendar.month_name[now.day % 12]
    day = len(participant.first_name) % 30

    return "{}. {}".format(day, month)


def get_like_amount(participant):
    first_part = str(sum_digits(int(participant.zip)))

    now = datetime.now()

    second_part = str(now.hour)

    return first_part + second_part


def sum_digits(n):
    s = 0
    while n:
        s += n % 10
        n //= 10
    return s


def get_share_decision(participant):
    now = datetime.now()

    return not participant.birthday.day == now.hour


def get_comment_decision(participant):
    birthday = participant.birthday

    as_datetime = datetime.combine(birthday, datetime.min.time())

    return num_years(as_datetime) >= 18


def num_years(begin, end=None):
    if end is None:
        end = datetime.now()
    num_years = int((end - begin).days / 365.25)
    if begin > years_ago(num_years, end):
        return num_years - 1
    else:
        return num_years


def years_ago(years, from_date=None):
    if from_date is None:
        from_date = datetime.now()
    try:
        return from_date.replace(year=from_date.year - years)
    except ValueError:
        # Must be 2/29!
        assert from_date.month == 2 and from_date.day == 29 # can be removed
        return from_date.replace(month=2, day=28,
                                 year=from_date.year-years)


def get_heart_decision(participant):
    session = get_session()

    murderer = session.query(Murderer).filter_by(participant=participant).first()

    session.close()

    return murderer is not None
