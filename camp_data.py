from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from camp_data_declarative import Base, Participant, TelegramUser, Admin

engine = create_engine('sqlite:///camp_data.db')
Base.metadata.bind = engine


def get_session():
    return scoped_session(sessionmaker(bind=engine))

def register_participant(telegram_id, authentication_code):
    session = get_session()
    participant = session.query(Participant).filter_by(authentication_code=authentication_code).first()
    participant.telegram_id = telegram_id

    register_regular_user(telegram_id, participant.first_name)

    session.commit()
    session.close()


def register_admin(telegram_id, call_name):
    session = get_session()

    admin = Admin(telegram_id=telegram_id)
    session.add(admin)

    register_regular_user(telegram_id, call_name)

    session.commit()
    session.close()


def is_admin(telegram_id):
    session = get_session()

    maybe_admin = session.query(Admin).filter_by(telegram_id=telegram_id).first()

    return maybe_admin is not None


def register_regular_user(telegram_id, call_name):
    session = get_session()

    telegram_user = TelegramUser(telegram_id=telegram_id, call_name=call_name)
    session.add(telegram_user)

    session.commit()
    session.close()
