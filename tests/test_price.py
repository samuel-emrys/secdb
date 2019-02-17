from secdb.symbol import Symbol
from secdb.currency import Currency
from secdb.exchange import Exchange
from sqlalchemy import create_engine
from secdb.database import Base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from secdb.application import import_vendors
from secdb.price import Price


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
    data_vendor_id = Column(Integer, ForeignKey('data_vendor.id'))
    symbol_id = Column(Integer, ForeignKey('symbol.id'))
    price_date = Column(TIMESTAMP)
    created_date = Column(TIMESTAMP)
    last_updated_date = Column(TIMESTAMP)
    open_price = Column(DECIMAL(19, 4))
    high_price = Column(DECIMAL(19, 4))
    low_price = Column(DECIMAL(19, 4))
    close_price = Column(DECIMAL(19, 4))
    adj_close_price = Column(DECIMAL(19, 4))
    volume = Column(BigInteger)
'''

vendors = import_vendors()

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

vts_price = Price(
    data_vendor_id=2,
    symbol_id=1,
    price_date=datetime.strptime("2018-12-01", "%Y-%m-%d"),
    created_date=datetime.utcnow(),
    last_updated_date=datetime.utcnow(),
    open_price=172.33,
    high_price=186.74,
    low_price=169.90,
    close_price=183.67,
    adj_close_price=None,
    volume=43122
    )


def test_insert_price():
    # Insert currency
    session.add(aud)

    # Insert Exchange
    session.add(asx)
    session.commit()

    for vendor in vendors:
        session.add(vendor)
        session.commit()

    # Insert Symbol
    session.add(vts)
    session.commit()

    # Insert Price
    session.add(vts_price)
    session.commit()


def test_read_prices():
    # Read
    prices = session.query(Price)
    for price in prices:
        print(price)


def test_update_price():
    # Update
    vts_price.volume=50000
    session.commit()
    test_read_prices()


def test_delete_price():
    # Delete
    # session.delete(vts)
    # session.commit()
    # session.delete(asx)
    # session.commit()
    # session.delete(aud)
    # session.commit()
    # print("Table contents deleted")
    pass
