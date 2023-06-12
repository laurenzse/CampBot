from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import csv
import hashlib
from camp_data import get_session

from camp_data_declarative import Base, Participant, LicenseInformation

session = get_session()

with open('participants.csv', 'r') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')

    buffer = []
    for row in csv_reader:
        buffer.append({
            'first_name': row[0],
            'last_name': row[1],
            'birthday': datetime.strptime(row[2], '%m/%d/%y').date(),
            'school_year': row[3],
            'zip': row[4],
            'city': row[5],
            'weather_id': row[6],
            'authentication_code': hashlib.sha256((row[0] + row[1] + row[2]).encode()).hexdigest()[:6]
        })
        if len(buffer) % 10000 == 0:
            session.bulk_insert_mappings(Participant, buffer)
            buffer = []

    session.bulk_insert_mappings(Participant, buffer)

session.commit()

with open('raw_images/places/licenses.csv', 'r') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')

    buffer = []
    for row in csv_reader:
        buffer.append({
            'file_path': row[0],
            'license': row[1],
            'author': row[2],
            'source': row[3],
            'link': row[4],
        })
        if len(buffer) % 10000 == 0:
            session.bulk_insert_mappings(LicenseInformation, buffer)
            buffer = []

    session.bulk_insert_mappings(LicenseInformation, buffer)

session.commit()
