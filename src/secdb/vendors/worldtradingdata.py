import io
import csv
import re
import requests
import json
import secdb.utils.helpers as helpers
from datetime import datetime
from secdb.utils.webio import WebIO
from secdb.vendors.vendor import Vendor
from lxml import html
from secdb.exchange import Exchange
from secdb.symbol import Symbol
from secdb.price import Price


class WorldTradingData(Vendor):
    def __init__(self, name, website_url, support_email, api):
        super(WorldTradingData, self).__init__(
            name, website_url, support_email, api
        )
        self.stock_url = "https://www.worldtradingdata.com/download/list"
        self.login_url = "https://www.worldtradingdata.com/login"
        self.historical_url = "https://www.worldtradingdata.com/api/v1/history"
        self.single_day_url = "https://www.worldtradingdata.com/api/v1/history\
        _multi_single_day"
        self.symbols = []
        self.exchanges = []

    def build_prices(self, symbols):
        # Since this is rate limited, just do as part of update function
        pass

    def build_currency(self):
        pass

    def build_symbols(self, currencies, exchanges):
        self.currencies = currencies

        session = WebIO.login(self.login_url)
        download = WebIO.download(url=self.stock_url, session=session)

        if download is None:
            return self.symbols

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

            if (exchange in exchanges) and (currency is not None):
                symbol_pair = (ticker, exchange)

                if symbol_pair not in existing_symbols:

                    symbol = Symbol(
                        exchange_code=exchange,
                        ticker=ticker,
                        name=name,
                        currency_code=currency,
                        created_date=now,
                        last_updated_date=now,
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
                    now = datetime.utcnow()
                    exchangeObj = Exchange(
                        abbrev=exchange,
                        suffix=suffix,
                        name=exchangeDesc,
                        created_date=now,
                        last_updated_date=now
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

    def update_price(self, symbols):
        pass

    def get_historical_prices(self):
        """
            Steps:
            1. get list of symbols
            2. find symbols in database with no data prior to created date
            3. for up to 250 symbols, get historical data
        """
        symbols = []
        for symbol in symbols:
            query_list = [
                self.api['historical']['url'],
                "?symbol=",
                symbol,
                "&sort=newest&api_token=",
                self.api['historical']['key']
            ]

            api_query = "".join(query_list)

            download = WebIO.download(api_query).decode('utf-8')
            json_prices = json.loads(download)

            # import aapl.json from tests/ to test parsing - limited to 250
            #  req/day

    def get_daily_prices(self):
        """
            Steps:
            1. get list of symbols
            2. find symbols in database with no data prior to created date
            3. Chunk into groups of 20 symbols and request all data
        """
        pass
