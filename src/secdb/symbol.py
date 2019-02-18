from secdb.database import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
'''
CREATE TABLE SYMBOL(
    id                      SERIAL                                              ,
    prev_id                 INTEGER             NULL                            ,
    exchange_code           VARCHAR(32)     NOT NULL                            ,
    ticker                  VARCHAR(32)     NOT NULL                            ,
    instrument              VARCHAR(64)         NULL                            ,
    name                    VARCHAR(255)        NULL                            ,
    sector                  VARCHAR(255)        NULL                            ,
    currency                VARCHAR(32)         NULL                            ,
    mer                     DECIMAL(13,10)      NULL                            ,
    benchmark               VARCHAR(255)        NULL                            ,
    listing_date            TIMESTAMP           NULL                            ,
    created_date            TIMESTAMP       NOT NULL                            ,
    last_updated_date       TIMESTAMP       NOT NULL                            ,
    UNIQUE                  (ticker, exchange_code)                             ,
    PRIMARY KEY             (id)                                                ,
    FOREIGN KEY             (exchange_code) REFERENCES      EXCHANGE(abbrev)    ,
    FOREIGN KEY             (prev_id)       REFERENCES      SYMBOL(id)          ,
    FOREIGN KEY             (currency)      REFERENCES      CURRENCY(code)
);

'''


class Symbol(Base):
    __tablename__ = 'symbol'

    id = Column(Integer, primary_key=True)
    prev_id = Column(Integer, ForeignKey('symbol.id'))
    exchange_code = Column(String, ForeignKey('exchange.abbrev'), nullable=False)
    ticker = Column(String, nullable=False)
    instrument = Column(String)
    name = Column(String)
    sector = Column(String)
    currency_code = Column(String, ForeignKey('currency.code'))
    mer = Column(String)
    benchmark = Column(String)
    listing_date = Column(TIMESTAMP)
    created_date = Column(TIMESTAMP, nullable=False)
    last_updated_date = Column(TIMESTAMP, nullable=False)

    # UniqueConstraint('customer_id', 'location_code', name='uix_1')

    # Relationship management
    # Symbol has many prices
    prices_daily = relationship('Price', backref='symbol')

    # def __init__(
    #     self,
    #     exchange_code,
    #     ticker,
    #     created_date,
    #     last_updated_date,
    #     prev_id=None,
    #     instrument=None,
    #     name=None,
    #     sector=None,
    #     currency_code=None,
    #     mer=None,
    #     benchmark=None,
    #     listing_date=None,
    # ):

    #     self.exchange_code = exchange_code
    #     self.ticker = ticker
    #     self.instrument = instrument
    #     self.name = name
    #     self.sector = sector
    #     self.currency_code = currency_code
    #     self.mer = mer
    #     self.benchmark = benchmark
    #     self.listing_date = listing_date
    #     self.created_date = created_date
    #     self.last_updated_date = last_updated_date
    #     self.prev_id = prev_id

    def __str__(self):
        out = [
            str(self.id),
            str(self.prev_id),
            str(self.exchange_code),
            str(self.ticker),
            str(self.instrument),
            str(self.name),
            str(self.sector),
            str(self.currency),
            str(self.mer),
            str(self.benchmark),
            str(self.listing_date),
            str(self.created_date),
            str(self.last_updated_date),
        ]
        return ",".join(out)

    def __eq__(self, other):
        if isinstance(other, Symbol):
            return (
                (self.exchange_code == other.exchange_code)
                and (self.ticker == other.ticker)
                )
        return False
