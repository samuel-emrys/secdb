from secdb.database import Base
from sqlalchemy import Column, Integer, BigInteger
from sqlalchemy.types import DECIMAL
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMP
'''
CREATE TABLE DAILY_PRICE(
    id                      SERIAL                                              ,
    data_vendor_id          INTEGER         NOT NULL                            ,
    symbol_id               INTEGER         NOT NULL                            ,
    price_date              TIMESTAMP       NOT NULL                            ,
    created_date            TIMESTAMP       NOT NULL                            ,
    last_updated_date       TIMESTAMP       NOT NULL                            ,
    open_price              DECIMAL(19,4)       NULL                            ,
    high_price              DECIMAL(19,4)       NULL                            ,
    low_price               DECIMAL(19,4)       NULL                            ,
    close_price             DECIMAL(19,4)       NULL                            ,
    adj_close_price         DECIMAL(19,4)       NULL                            ,
    volume                  BIGINT              NULL                            ,
    PRIMARY KEY             (id)                                                ,
    FOREIGN KEY             (data_vendor_id)    REFERENCES DATA_VENDOR(id)      ,
    FOREIGN KEY             (symbol_id)         REFERENCES SYMBOL(id)           
);

'''
class Price(Base):
    __tablename__ = 'daily_price'

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


    def __init__(
        self,
        vendor,
        symbol,
        price_date,
        created_date,
        last_updated_date,
        open_price=None,
        high_price=None,
        low_price=None,
        close_price=None,
        adj_close_price=None,
        volume=None,
    ):

        self.vendor = vendor
        self.symbol = symbol
        self.price_date = price_date
        self.created_date = created_date
        self.last_updated_date = last_updated_date
        self.open_price = open_price
        self.high_price = high_price
        self.low_price = low_price
        self.close_price = close_price
        self.adj_close_price = adj_close_price
        self.volume = volume

    def __str__(self):
        out = [
            str(self.vendor),
            str(self.symbol),
            str(self.price_date),
            str(self.created_date),
            str(self.last_updated_date),
            str(self.open_price),
            str(self.high_price),
            str(self.low_price),
            str(self.close_price),
            str(self.adj_close_price),
            str(self.volume),
        ]
        return ",".join(out)
