from camp_data import get_session
from camp_data_declarative import Participant
from utils import post_screenshot
from code_challenge_generator import generate_challenge
from datetime import datetime

CAMP_START = datetime(year=2019, month=8, day=7, hour=12)
CAMP_END = datetime(year=2019, month=8, day=10, hour=23)


def distribute_challenges(bot):
    camp_progression = (datetime.now() - CAMP_START).total_seconds()/(CAMP_END - CAMP_START).total_seconds()
    camp_progression = min(max(camp_progression, 0), 1)
    # camp_progression = 1

    session = get_session()

    registered_participants = session.query(Participant).filter(Participant.telegram_id.isnot(None)).all()

    for participant in registered_participants:
        challenge_post_path = generate_challenge(participant.id, camp_progression)

        post_screenshot(bot, participant.telegram_id, challenge_post_path)
