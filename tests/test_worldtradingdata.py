from secdb.application import import_vendors

vendors = import_vendors()

for vendor in vendors:
    if vendor.name == 'World Trading Data':
        wtd = vendor
    elif vendor.name == 'Currency-ISO':
        ciso = vendor


def test_build_exchanges():
    wtd.build_exchanges()

    print("Number of exchanges: " + str(len(wtd.exchanges)))
    assert len(wtd.exchanges) == 40


def test_build_symbols():
    currencies = ciso.build_currency()

    wtd.build_symbols(currencies, wtd.exchanges)
    print("Symbol array length: " + str(len(wtd.symbols)))

    assert len(wtd.symbols) > 0
