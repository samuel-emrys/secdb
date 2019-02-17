from abc import abstractmethod
from datetime import datetime
from datetime import timedelta
from secdb.database import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship

import secdb.utils.helpers as helpers
import re

'''
CREATE TABLE DATA_VENDOR(
    id                      SERIAL                  ,
    name                    VARCHAR(64)     NOT NULL,
    website_url             VARCHAR(255)        NULL,
    support_email           VARCHAR(255)        NULL,
    api_url                 VARCHAR(255)        NULL,
    api_key                 VARCHAR(255)        NULL,
    created_date            TIMESTAMP       NOT NULL,
    last_updated_date       TIMESTAMP       NOT NULL,
    PRIMARY KEY             (id)
);
'''


class Vendor(Base):
    __tablename__ = 'data_vendor'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    website_url = Column(String)
    support_email = Column(String)
    created_date = Column(TIMESTAMP)
    last_updated_date = Column(TIMESTAMP)

    # Relationship management
    # Data vendor has many prices
    prices_daily = relationship('Price', backref='vendor')

    # Abstract vendor class, individual vendors inherit from this

    # Constructor
    def __init__(
        self, name, website_url, support_email, api,
        created_date=datetime.utcnow(), last_updated_date=datetime.utcnow()
    ):
        self.name = name
        self.website_url = website_url
        self.support_email = support_email
        self.api = api
        self.created_date = created_date
        self.last_updated_date = last_updated_date

    # String cast overload
    def __str__(self):

        out = [
            str(self.id),
            str(self.name),
            str(self.website_url),
            str(self.support_email),
            str(self.created_date),
            str(self.last_updated_date)
        ]
        return ",".join(out)

    def __eq__(self, other):
        return (self.name == other.name)

    # Symbol Helper methods
    def parse_vendor(element):
        element = helpers.removeWhitespace(element)

        if element == "NA" or element == "":
            return None

        return element

    def parseTicker(self, ticker):
        # Remove extraneous white space from left and right of string, and
        # remove tabs/new line characters from middle of string
        ticker = helpers.removeWhitespace(ticker)

        # Could also check that it contains only uppercase characters, length
        # 3-5 (what's the maximum ticker length?)
        return ticker

    def parseInstrument(self, instrument):
        # Remove extraneous white space from left and right of string, and
        # remove tabs/new line characters from middle of string
        instrument = helpers.removeWhitespace(instrument)

        return instrument

    def parseName(self, name):
        # Remove extraneous white space from left and right of string, and
        # remove tabs/new line characters from middle of string
        name = helpers.removeWhitespace(name)

        return name

    def parseSector(self, sector):
        if (sector is not None):
            # Remove extraneous white space from left and right of string, and
            # remove tabs/new line characters from middle of string
            sector = helpers.removeWhitespace(sector)

            if sector == "#" or sector == "Not Applic":
                sector = None

        return sector

    def parseCurrency(self, currency):

        if currency not in self.currencies:
            currency = None

        return currency

    def parseMER(self, mer):
        if (mer is not None):
            # Remove extraneous white space from left and right of string, and
            # remove tabs/new line characters from middle of string
            mer = helpers.removeWhitespace(mer)

            if mer == "-":
                mer = None
                # else if string doesn't match a decimal
            elif not (re.match(r"^[0-9]{1,2}(.[0-9]+?)?$", mer)):
                # now = datetime.utcnow()
                mer = None

        return mer

    def parseBenchmark(self, benchmark):
        if (benchmark is not None):
            # Remove extraneous white space from left and right of string, and
            # remove tabs/new line characters from middle of string
            benchmark = helpers.removeWhitespace(benchmark)

            if benchmark == "-":
                benchmark = None

        return benchmark

    def parse_date(self, date, date_format):

        # Remove extraneous white space from left and right of string, and
        # remove tabs/new line characters from middle of string
        date_str = helpers.removeWhitespace(date)

        try:
            date = datetime.strptime(date_str, date_format)

        except ValueError:
            date = None

        return date

        # Exchange Helper Methods
        # @TODO: Put these in Exchange class, refactor method of parsing
        # Actually, maybe I should make a vendor for wikipedia... content
        # scraped from wikipedia should be parsed by the grabbing object

    def parseName(self, name):
        name = helpers.removeWhitespace(name)
        name = helpers.removeWikipediaReferences(name)

        return name

    def parseAbbr(self, abbr):
        abbr = helpers.removeWhitespace(abbr)
        abbr = helpers.removeWikipediaReferences(abbr)
        return abbr

    def parseCountry(self, country):
        country = helpers.removeWhitespace(country)
        country = helpers.removeWikipediaReferences(country)
        return country

    def parseCity(self, city):
        city = helpers.removeWhitespace(city)
        city = helpers.removeWikipediaReferences(city)
        return city

    def parseTimezone(self, timezone):
        timezone = helpers.removeWhitespace(timezone)
        timezone = helpers.removeWikipediaReferences(timezone)
        return timezone

    def parseTZOffset(self, delta):
        delta = helpers.removeWhitespace(delta)
        delta = helpers.removeWikipediaReferences(delta)
        delta = delta.replace("−", "-")
        delta = timedelta(hours=float(delta))

        return delta

    def parseDST(self, dst):
        dst = helpers.removeWhitespace(dst)
        dst = helpers.removeWikipediaReferences(dst)
        return dst

    def parseTime(self, time):
        time = helpers.removeWhitespace(time)
        time = helpers.removeWikipediaReferences(time)
        time = datetime.strptime(time, "%H:%M").time()

        return time

        # Price Helper Methods

    def parse_price(self, price):
        price = helpers.removeWhitespace(price)
        price = price.replace("$", "")

        return price

    # Build methods
    @abstractmethod
    def build_symbols(self, currencies, exchanges):
        pass

    @abstractmethod
    def build_prices(self, symbols):
        pass

    @abstractmethod
    def build_currency(self):
        pass

    @abstractmethod
    def build_exchanges(self):
        pass

        # Update methods

    @abstractmethod
    def update_symbols(self):
        pass

    @abstractmethod
    def update_prices(self):
        pass

    @abstractmethod
    def update_currency(self):
        pass

    @abstractmethod
    def update_exchanges(self):
        pass
