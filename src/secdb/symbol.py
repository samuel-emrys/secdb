from secdb.database import Base


class Symbol(Base):
    def __init__(
        self,
        exchange_code,
        ticker,
        created_date,
        last_updated_date,
        instrument=None,
        name=None,
        sector=None,
        currency=None,
        mer=None,
        benchmark=None,
        listing_date=None,
    ):

        self.exchange_code = exchange_code
        self.ticker = ticker
        self.instrument = instrument
        self.name = name
        self.sector = sector
        self.currency = currency
        self.mer = mer
        self.benchmark = benchmark
        self.listing_date = listing_date
        self.created_date = created_date
        self.last_updated_date = last_updated_date

    def __str__(self):
        out = [
            self.exchange_code,
            self.ticker,
            self.instrument,
            self.name,
            self.sector,
            self.currency,
            self.mer,
            self.benchmark,
            self.listing_date,
            self.created_date,
            self.last_updated_date,
        ]
        return ",".join(out)
