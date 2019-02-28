from secdb.vendors.vendor import Vendor
from secdb.currency import Currency
from secdb.exchange import Exchange
from secdb.symbol import Symbol
from secdb.price import Price
import secdb.database

session = secdb.database.connect()


def test_query_currency():
    aud = session.query(Currency).filter(Currency.code=='AUD').first()
    # print(aud)
    assert aud is not None


def test_all_currencies():
    currencies = session.query(Currency).all()
    # print(currencies)
    assert currencies is not []


def test_query_exchange():
    asx = session.query(Exchange).filter(Exchange.abbrev=='ASX').first()
    # print(asx)
    assert asx is not None


def test_query_symbol():
    vas = session.query(Symbol).filter(Symbol.ticker=='VAS').first()
    # print(vas)
    assert vas is not None


def test_query_vendor():
    vendor = session.query(Vendor).filter(Vendor.name=='Australian Stock Exchange').first()
    # print(vendor)
    assert vendor is not None
