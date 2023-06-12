from sqlalchemy import Column, ForeignKey, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class TelegramUser(Base):
    __tablename__ = 'telegram_users'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    telegram_id = Column(Integer, primary_key=True)
    call_name = Column(String(250), nullable=False)


class Participant(Base):
    __tablename__ = 'participants'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)
    first_name = Column(String(250), nullable=False)
    last_name = Column(String(250), nullable=False)
    birthday = Column(Date, nullable=False)
    school_year = Column(Integer, nullable=False)
    zip = Column(String(250), nullable=False)
    city = Column(String(250), nullable=False)
    weather_id = Column(String(250), nullable=False)
    telegram_id = Column(Integer, ForeignKey('telegram_users.telegram_id'))
    telegram_user = relationship(TelegramUser)
    authentication_code = Column(String(250), nullable=False)


class Admin(Base):
    __tablename__ = 'admins'
    telegram_id = Column(Integer, ForeignKey('telegram_users.telegram_id'), primary_key=True)
    telegram_user = relationship(TelegramUser)


class LicenseInformation(Base):
    __tablename__ = 'license_information'
    file_path = Column(String, primary_key=True, nullable=False)
    license = Column(String)
    author = Column(String)
    source = Column(String)
    link = Column(String)


class Murderer(Base):
    __tablename__ = 'murderers'
    participant_id = Column(Integer, ForeignKey('participants.id'), primary_key=True)
    participant = relationship(Participant, foreign_keys=[participant_id])
    victim_id = Column(Integer, ForeignKey('participants.id'), nullable=False)
    victim = relationship(Participant, foreign_keys=[victim_id])


# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('sqlite:///camp_data.db')

# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)