from secdb.database import Base
from sqlalchemy import Column, Integer, BigInteger
from sqlalchemy.types import DECIMAL
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import TIMESTAMP
'''
CREATE TABLE DAILY_PRICE(
    id                      SERIAL                                            ,
    data_vendor_id          INTEGER         NOT NULL                          ,
    symbol_id               INTEGER         NOT NULL                          ,
    price_date              TIMESTAMP       NOT NULL                          ,
    created_date            TIMESTAMP       NOT NULL                          ,
    last_updated_date       TIMESTAMP       NOT NULL                          ,
    open_price              DECIMAL(19,4)       NULL                          ,
    high_price              DECIMAL(19,4)       NULL                          ,
    low_price               DECIMAL(19,4)       NULL                          ,
    close_price             DECIMAL(19,4)       NULL                          ,
    adj_close_price         DECIMAL(19,4)       NULL                          ,
    volume                  BIGINT              NULL                          ,
    PRIMARY KEY             (id)                                              ,
    FOREIGN KEY             (data_vendor_id)    REFERENCES DATA_VENDOR(id)    ,
    FOREIGN KEY             (symbol_id)         REFERENCES SYMBOL(id)
);
'''


class Price(Base):
    __tablename__ = 'daily_price'

    id = Column(Integer, primary_key=True)
    data_vendor_id = Column(Integer, ForeignKey('data_vendor.id'), nullable=False)
    symbol_id = Column(Integer, ForeignKey('symbol.id'), nullable=False)
    price_date = Column(TIMESTAMP)
    open_price = Column(DECIMAL(19, 4))
    high_price = Column(DECIMAL(19, 4))
    low_price = Column(DECIMAL(19, 4))
    close_price = Column(DECIMAL(19, 4))
    adj_close_price = Column(DECIMAL(19, 4))
    volume = Column(BigInteger)
    created_date = Column(TIMESTAMP)
    last_updated_date = Column(TIMESTAMP)

    vendor = relationship('Vendor', back_populates='prices_daily')
    symbol = relationship('Symbol', back_populates='prices_daily')

    def __str__(self):
        out = [
            str(self.data_vendor_id),
            str(self.symbol_id),
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
