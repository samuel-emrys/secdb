from secdb.application import import_vendors
from secdb.exchange import Exchange
import secdb.database

vendors = import_vendors()

for vendor in vendors:
    if vendor.name == 'Australian Stock Exchange':
        asx = vendor
    elif vendor.name == 'Currency-ISO':
        ciso = vendor

asx.currencies = ciso.build_currency()
session = secdb.database.connect()


# def test_build_exchange_products():
#     asx.build_exchange_products()
#     print("Number of exchange products: " + str(len(asx.symbols)))

#     assert len(asx.symbols) > 0


# def test_build_companies():
#     asx.symbols = []
#     asx.build_companies()
#     print("Number of companies: " + str(len(asx.symbols)))

#     assert len(asx.symbols) > 0


def test_build_symbols():
    exchanges = session.query(Exchange).all()
    asx.symbols = []
    asx.build_symbols(currencies=asx.currencies, exchanges=exchanges)

    print("Number of symbols: " + str(len(asx.symbols)))
    assert len(asx.symbols) > 0


def test_build_prices():

    asx.build_prices(asx.symbols, session)

    assert len(asx.prices) == 0
