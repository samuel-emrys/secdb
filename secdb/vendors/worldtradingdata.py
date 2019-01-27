import io
import csv
import re
import requests
import utils.helpers as helpers
from datetime import datetime
from utils.webio import WebIO
from vendors.vendor import Vendor
from lxml import html
from exchange import Exchange
from currency import Currency
from symbol import Symbol
from price import Price


class VendorWorldTradingData(Vendor):
    def __init__(self, name, website_url, support_email, api_url, api_key):
        super(VendorWorldTradingData, self).__init__(
            name, website_url, support_email, api_url, api_key
        )
        self.stock_url = "https://www.worldtradingdata.com/download/list"
        self.login_url = "https://www.worldtradingdata.com/login"
        self.symbols = []
        self.exchanges = []

    def build_price(self, symbols):
        pass

    def build_currency(self):
        pass

    def build_symbols(self, currencies, exchanges):
        self.currencies = currencies

        session = WebIO.login(self.login_url)
        download = WebIO.download(url=self.stock_url, session=session)
        csvfile = io.StringIO(download.decode("utf-8"))
        stocklist = csv.reader(csvfile)
        existing_symbols = [(x.ticker, x.exchange_code) for x in self.symbols]

        # Parse symbols in the stocklist, and add them to list for addition to
        # database
        for line in stocklist:

            exchange = helpers.removeWhitespace(line[4])
            name = helpers.removeWhitespace(line[1])
            currency = helpers.removeWhitespace(line[2])
            currency = self.parseCurrency(currency)
            ticker_list = line[0].split(".")

            ticker = (
                helpers.removeWhitespace("".join(ticker_list[:-1]))
                if len(ticker_list) > 1
                else helpers.removeWhitespace(ticker_list[0])
            )

            now = datetime.utcnow()
            created_date = now
            last_updated_date = now

            if (exchange in exchanges) and (currency is not None):
                symbol_pair = (ticker, exchange)

                if symbol_pair not in existing_symbols:

                    symbol = Symbol(
                        exchange_code=exchange,
                        ticker=ticker,
                        name=name,
                        currency=currency,
                        created_date=created_date,
                        last_updated_date=last_updated_date,
                    )

                    self.symbols.append(symbol)
                    existing_symbols.append(symbol_pair)

        return self.symbols

    def build_exchanges(self):

        # Login and download file
        session = WebIO.login(self.login_url)
        download = WebIO.download(url=self.stock_url, session=session)

        # Read file as csv in memory
        csvfile = io.StringIO(download.decode("utf-8"))
        stocklist = csv.reader(csvfile)

        # Create map of exchanges to count multiple instances of each
        exchangeCount = {}

        # Create dataset of suffixes
        for line in stocklist:

            exchange = helpers.removeWhitespace(line[4])
            exchangeDesc = helpers.removeWhitespace(line[3])
            suffixList = line[0].split(".")
            suffixToken = helpers.removeWhitespace(suffixList[-1])

            if (
                suffixToken == "A"
                or suffixToken == "B"
                or suffixToken == "C"
                or suffixToken == "V"
                or len(suffixList) == 1
            ):
                suffix = None
            else:
                suffix = suffixToken

            if (
                (exchange != "N/A")
                and (not re.match(r"(.*?)INDEX(.*)", exchange))
                and (" " not in exchange)
            ):
                exchangeCount[exchange] = exchangeCount.get(exchange, 0) + 1
                if exchangeCount[exchange] == 1:
                    exchangeObj = Exchange(
                        abbrev=exchange, suffix=suffix, name=exchangeDesc
                    )
                    self.exchanges.append(exchangeObj)

        self.addTZData()

        return self.exchanges

    def addTZData(self):

        DATA_ROW_LENGTH = 13

        exchangeWikiURL = "https://en.wikipedia.org/wiki/\
        List_of_stock_exchange_trading_hours"
        page = requests.get(exchangeWikiURL)
        tree = html.fromstring(page.content)
        tr_elements = tree.xpath("//tr")
        wiki_exchanges = {}

        for row in tr_elements:

            first_element = helpers.removeWhitespace(row[0].text_content())

            if len(row) == DATA_ROW_LENGTH and first_element != "Name":
                name = self.parseName(row[0].text_content())
                abbr = self.parseAbbr(row[1].text_content())
                country = self.parseCountry(row[2].text_content())
                city = self.parseCity(row[3].text_content())
                zone = self.parseTimezone(row[4].text_content())
                delta = self.parseTZOffset(row[5].text_content())
                dst = self.parseDST(row[6].text_content())
                open_local = self.parseTime(row[7].text_content())
                close_local = self.parseTime(row[8].text_content())
                open_utc = self.parseTime(row[10].text_content())
                close_utc = self.parseTime(row[11].text_content())

                wiki_exchanges[abbr] = Exchange(
                    abbrev=abbr,
                    name=name,
                    city=city,
                    country=country,
                    timezone=zone,
                    timezone_offset=delta,
                    open_utc=open_utc,
                    close_utc=close_utc,
                )

        for exchange in self.exchanges:

            exchangeData = wiki_exchanges.get(exchange.abbrev, None)

            if (exchangeData is not None):

                exchange.city = exchangeData.city
                exchange.country = exchangeData.country
                exchange.timezone = exchangeData.timezone
                exchange.timezone_offset = exchangeData.timezone_offset
                exchange.open_utc = exchangeData.open_utc
                exchange.close_utc = exchangeData.close_utc
