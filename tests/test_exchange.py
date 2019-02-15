from secdb.exchange import Exchange
from sqlalchemy import create_engine
from secdb.database import Base
from sqlalchemy.orm import sessionmaker
from datetime import datetime


'''
    Initialisation variables
'''
db_host = "localhost"
db_user = "postgres"
db_pass = ""
db_name = "securities_master"

db_string = "postgresql://"+db_user+":"+db_pass+"@"+db_host+"/"+db_name
db = create_engine(db_string)

Session = sessionmaker(db)
session = Session()
Base.metadata.create_all(db)

asx = Exchange(
        abbrev='ASX',
        suffix='AX',
        name='Australian Securities Exchange',
        city='Sydney',
        country='Australia',
        timezone='AEST',
        timezone_offset=datetime.strptime("10:00:00", "%H:%M:%S").time(),
        open_utc=datetime.strptime("00:00:00", "%H:%M:%S").time(),
        close_utc=datetime.strptime("06:00:00", "%H:%M:%S").time()
    )


def test_insert_exchange():
    # Insert
    session.add(asx)
    session.commit()


def test_read_exchanges():
    # Read
    exchanges = session.query(Exchange)
    for exchange in exchanges:
        print(exchange)


def test_update_exchange():
    # Update
    asx.name = "Non-Australian Securities Exchange"
    session.commit()
    test_read_exchanges()


def test_delete_exchange():
    # Delete
    session.delete(asx)
    session.commit()
