from secdb.aggregator import Aggregator
from secdb.application import import_vendors
import secdb.database


session = secdb.database.connect()
agg = Aggregator(session)


def test_vendor_add():
    vendors = import_vendors()

    agg.import_vendors(vendors)


def test_currency_add():
    currencies = []
    for vendor in agg.vendors:
        currencies.append(vendor.build_currency())
    agg.import_currencies(currencies)


def test_exchange_add():
    exchanges = []
    for vendor in agg.vendors:
        exchanges.append(vendor.build_exchanges())
    agg.import_exchanges(exchanges)


def test_symbol_add():
    symbols = []
    for vendor in agg.vendors:
        symbols.append(vendor.build_symbols(agg.currencies, agg.exchanges))
    agg.import_symbols(symbols)

    # for vendor in agg.vendors:

    # pass


def test_price_add():
    pass
