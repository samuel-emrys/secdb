
class Aggregator:
    """
    This class is the authoritative source of all data. This class will parse
    the data and aggregate it into one set, ensuring that there are no errors
    or duplicates, and it is as complete as possible
    """

    def __init__(self, session):
        self.session = session
        self.currencies = []
        # self.symbols = []
        self.symbols = []
        self.exchanges = []
        self.prices = []
        self.vendors = []

    def import_vendors(self, vendors):

        self.vendors = vendors

        self.session.bulk_save_objects(self.vendors)
        self.session.commit()

    def import_currencies(self, currencies):

        # Remove empty list elements
        currencies = [x for x in currencies if x is not None]

        # Consolidate currencies into unique list
        currset = set()
        for source in currencies:
            currset.update(source)
        self.currencies = list(currset)

        # Insert to database
        self.session.bulk_save_objects(self.currencies)
        self.session.commit()

    def import_symbols(self, symbols):
        # Remove empty lists (caused by vendors not providing a symbol list)
        symbols = [x for x in symbols if x is not None]

        # Consolidate symbols into unique list
        symset = set()
        for source in symbols:
            symset.update(source)
        self.symbols = list(symset)

        # Insert symbols to database
        self.session.bulk_save_objects(self.symbols)
        self.session.commit()

    def import_exchanges(self, exchanges):
        """
        @TODO
        Improve matching between suffix and stock exchanges. Specific
        attention:
                - Sao Paolo Stock Exchange
                - New Zealand Stock Exchange
                - Frankfurt Stock Exchange
        Consider using regex to match first, first and second, first second
        third words
        - Potentially develop confidence list and choose more confident if
        above threshold
            - Dynamic programming?
            - Look into techniques
        """
        # Remove empty list elements
        exchanges = [x for x in exchanges if x is not None]

        # Consolidate symbols into unique list
        exchset = set()
        for source in exchanges:
            exchset.update(source)
        self.exchanges = list(exchset)

        # Insert to database
        self.session.bulk_save_objects(self.exchanges)
        self.session.commit()

    def import_prices(self, prices):
        # Due to data size and RAM constraints, prices are inserted directly to
        # database from vendors
        pass
