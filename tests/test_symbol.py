from secdb.symbol import Symbol
from secdb.currency import Currency
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

'''
    id = Column(Integer, primary_key=True)
    prev_id = Column(Integer, ForeignKey('symbol.id'))
    exchange_code = Column(String, ForeignKey('exchange.abbrev'))
    ticker = Column(String)
    instrument = Column(String)
    name = Column(String)
    sector = Column(String)
    currency = Column(String, ForeignKey('currency.code'))
    mer = Column(String)
    benchmark = Column(String)
    listing_date = Column(TIMESTAMP)
    created_date = Column(TIMESTAMP)
    last_updated_date = Column(TIMESTAMP)
'''
asx = Exchange(
        abbrev='ASX',
        suffix='AX',
        name='Australian Securities Exchange',
        city='Sydney',
        country='Australia',
        timezone='AEST',
        timezone_offset=datetime.strptime("10:00:00", "%H:%M:%S").time(),
        open_utc=datetime.strptime("00:00:00", "%H:%M:%S").time(),
        close_utc=datetime.strptime("06:00:00", "%H:%M:%S").time(),
        created_date=datetime.utcnow(),
        last_updated_date=datetime.utcnow()
    )

aud = Currency(
        code='AUD',
        num=36,
        minor_unit=2,
        name='Australian Dollar'
    )

vts = Symbol(

        prev_id=None,
        exchange_code='ASX',
        ticker='VTS',
        instrument='ETF',
        name='Vanguard Total US Stock Market Index ETF',
        sector=None,
        currency='AUD',
        mer='0.05%',
        benchmark='MSCI Total US Stock Market Index',
        listing_date=datetime.strptime("2009-12-01", "%Y-%m-%d"),
        created_date=datetime.utcnow(),
        last_updated_date=datetime.utcnow()

    )


def test_insert_symbol():
    # Insert currency
    session.add(aud)

    # Insert Exchange
    session.add(asx)
    session.commit()

    # Insert Symbol
    session.add(vts)
    session.commit()


def test_read_symbols():
    # Read
    symbols = session.query(Symbol)
    for symbol in symbols:
        print(symbol)


def test_update_price():
    # Update
    vts.name = "Non-Vanguard Total US Stock Market Index ETF"
    session.commit()
    test_read_symbols()


def test_delete_price():
    # Delete
    session.delete(vts)
    session.commit()
    session.delete(asx)
    session.commit()
    session.delete(aud)
    session.commit()
    print("Table contents deleted")
