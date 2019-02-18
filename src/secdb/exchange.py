from secdb.database import Base
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import TIME, TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime


'''
CREATE TABLE EXCHANGE(
    abbrev                  VARCHAR(32)     NOT NULL UNIQUE                   ,
    suffix                  VARCHAR(32)         NULL                          ,
    name                    VARCHAR(255)    NOT NULL                          ,
    city                    VARCHAR(255)        NULL                          ,
    country                 VARCHAR(255)        NULL                          ,
    timezone                VARCHAR(64)         NULL                          ,
    timezone_offset         TIME                NULL                          ,
    open_time               TIME                NULL                          ,
    close_time              TIME                NULL                          ,
    created_date            TIMESTAMP       NOT NULL                          ,
    last_updated_date       TIMESTAMP       NOT NULL                          ,
    PRIMARY KEY             (abbrev)
);
'''


class Exchange(Base):
    __tablename__ = 'exchange'

    abbrev = Column(String, primary_key=True)
    suffix = Column(String)
    name = Column(String)
    city = Column(String)
    country = Column(String)
    timezone = Column(String)
    timezone_offset = Column(TIME)
    open_utc = Column(TIME)
    close_utc = Column(TIME)
    created_date = Column(TIMESTAMP)
    last_updated_date = Column(TIMESTAMP)

    # Relationship managment
    # Exchange has many symbols
    symbols = relationship('Symbol', backref='exchange')

    def __str__(self):

        out = [
            str(self.abbrev),
            str(self.suffix),
            str(self.name),
            str(self.city),
            str(self.country),
            str(self.timezone),
            str(self.timezone_offset),
            str(self.open_utc),
            str(self.close_utc)
        ]
        return ",".join(out)

    def __eq__(self, other):
        if isinstance(other, Exchange):
            return (self.abbrev == other.abbrev)
        return False
