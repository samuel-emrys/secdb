import io
import json
import csv
import requests
from lxml import html
from datetime import datetime
from datetime import time

from utils.webio import WebIO
from vendors.vendor import Vendor
import utils.helpers as helpers

from symbol import Symbol
from price import Price


class ASX(Vendor):
    def __init__(self, name, website_url, support_email, api):

        super(ASX, self).__init__(
            name, website_url, support_email, api
        )
        self.company_url = "https://www.asx.com.au/asx/research/"
        self.company_file = "ASXListedCompanies.csv"
        self.etp_url = "https://www.asx.com.au/products/etf/\
        managed-funds-etp-product-list.htm"
        self.symbols = []
        self.prices = []

    def build_currency(self):
        pass

    def build_prices(self, symbols):
        symbols_au = [x for x in self.symbols if x.exchange_code == "ASX"]

        for symbol in symbols_au:
            query = self.api_url.replace("SYMBOL", symbol.ticker)

            download = WebIO.download(query).decode("utf-8")

            # Handles rate limiting of site
            while "<!DOCTYPE html>" in download:
                download = WebIO.download(query).decode("utf-8")
                time.sleep(35)

            if (
                ("id-or-code-invalid" not in download)
                and (download is not None)
            ):
                print(symbol.ticker)
                try:
                    json_prices = json.loads(download)

                except json.decoder.JSONDecodeError:
                    print(download)
                    break

                for field in json_prices:
                    for price_dict in json_prices[field]:
                        now = datetime.utcnow()
                        # This date needs to have timezone information.
                        # currently being truncated in conversion
                        date_str = price_dict["close_date"]
                        date_str = date_str.split("T")[0]
                        price_date = self.parse_date(date_str, "%Y-%m-%d")
                        ticker = price_dict["code"]
                        open_price = (
                            price_dict["close_price"]
                            - price_dict["change_price"]
                        )
                        high_price = price_dict["day_high_price"]
                        low_price = price_dict["day_low_price"]
                        close_price = price_dict["close_price"]
                        volume = price_dict["volume"]

                        if price_date is not None:
                            price = Price(
                                vendor=ASX,
                                price_date=price_date,
                                symbol=ticker,
                                created_date=now,
                                last_updated_date=now,
                                open_price=open_price,
                                high_price=high_price,
                                low_price=low_price,
                                close_price=close_price,
                                volume=volume,
                            )

                            self.prices.append(price)

    def build_exchanges(self):
        pass

    def build_symbols(self, currencies, exchanges):
        self.currencies = currencies
        self.build_companies()
        self.build_exchange_products()

        return self.symbols

    def build_companies(self):

        download = WebIO.download(url=self.company_url, file=self.company_file)
        download = download.decode("utf-8")
        csvfile = io.StringIO(download, newline="")
        companies = csv.reader(csvfile)

        instrument = "Shares"
        currency = "AUD"
        exchange = "ASX"
        MER = None
        benchmark = None
        existing_symbols = [(x.ticker, x.exchange_code) for x in self.symbols]

        count = 0
        for company in companies:
            # count the number of lines before entries should be entered
            # (truncates first 3 lines)
            count += 1

            if len(company) > 0 and count > 3:
                ticker = None
                name = company[0]
                sector = None
                if len(company) == 2:
                    ticker = company[1]
                elif len(company) == 3:
                    ticker = company[1]
                    sector = company[2]

                sector = self.parseSector(sector)
                now = datetime.utcnow()
                created_date = now
                last_updated_date = now
                symbol_pair = (ticker, exchange)

                # Create symbol object to add to list
                if symbol_pair not in existing_symbols:

                    symbol = Symbol(
                        exchange_code=exchange,
                        ticker=ticker,
                        instrument=instrument,
                        name=name,
                        sector=sector,
                        currency=currency,
                        mer=MER,
                        benchmark=benchmark,
                        created_date=created_date,
                        last_updated_date=last_updated_date,
                    )

                    self.symbols.append(symbol)
                    existing_symbols.append(symbol_pair)

    def build_exchange_products(self):

        page = requests.get(self.etp_url)
        tree = html.fromstring(page.content)
        tr_elements = tree.xpath("//tr")

        # Initialise table entry values
        table_format = ""
        sector = None
        currency = "AUD"
        exchange = "ASX"
        existing_symbols = [(x.ticker, x.exchange_code) for x in self.symbols]

        for row in tr_elements:
            first_element = helpers.removeWhitespace(row[0].text_content())

            # Identify which table is being parsed and define table format
            if first_element == "Exposure":
                if len(row) == 9:
                    table_format = "LIC"
                elif len(row) == 6:
                    table_format = "AREITS"
                elif (
                    len(row) == 10
                    and helpers.removeWhitespace(row[3].text_content())
                    == "iNAV Code"
                ):
                    table_format = "ETP"
                else:
                    table_format = "ETP_SINGLE_ASSET"

            elif first_element == "Name":
                if len(row) == 7:
                    table_format = "INFRASTRUCTURE"
                elif len(row) == 8:
                    table_format = "ABS_RETURN_FUNDS"
                elif len(row) == 6:
                    table_format = "PDFs"

            # Store the row contents based on the identified table format
            else:
                if len(row) == 1:
                    # Sector is on its own line, so parse length 1 lines to
                    # obtain sector for following entries
                    sector = row[0].text_content()

                elif table_format == "LIC":

                    name = row[0].text_content()
                    ticker = row[1].text_content()
                    instrument = row[2].text_content()
                    benchmark = row[3].text_content()
                    mer = row[4].text_content()
                    listing_date = row[6].text_content()

                elif table_format == "AREITS":

                    name = row[0].text_content()
                    ticker = row[1].text_content()
                    instrument = row[2].text_content()
                    benchmark = None
                    mer = None
                    listing_date = row[3].text_content()

                elif table_format == "ETP":

                    name = row[0].text_content()
                    ticker = row[1].text_content()
                    instrument = row[2].text_content()
                    benchmark = row[4].text_content()
                    mer = row[6].text_content()
                    listing_date = row[7].text_content()

                elif table_format == "ETP_SINGLE_ASSET":

                    name = row[0].text_content()
                    ticker = row[1].text_content()
                    instrument = row[2].text_content()
                    benchmark = row[4].text_content()
                    mer = row[6].text_content()
                    listing_date = row[7].text_content()

                elif table_format == "INFRASTRUCTURE":
                    name = row[0].text_content()
                    ticker = row[1].text_content()
                    instrument = row[2].text_content()
                    sector = row[3].text_content()
                    benchmark = None
                    mer = None
                    listing_date = row[4].text_content()

                elif table_format == "ABS_RETURN_FUNDS":

                    name = row[0].text_content()
                    ticker = row[1].text_content()
                    instrument = row[2].text_content()
                    sector = None
                    benchmark = row[3].text_content()
                    mer = row[4].text_content()
                    listing_date = row[5].text_content()

                elif table_format == "PDFs":
                    name = row[0].text_content()
                    ticker = row[1].text_content()
                    instrument = row[2].text_content()
                    sector = None
                    benchmark = None
                    mer = None
                    listing_date = row[3].text_content()

                if len(row) > 1:

                    ticker = self.parseTicker(ticker)
                    instrument = self.parseInstrument(instrument)
                    name = self.parseName(name)
                    sector = self.parseSector(sector)
                    currency = self.parseCurrency(currency)
                    mer = self.parseMER(mer)
                    benchmark = self.parseBenchmark(benchmark)
                    listing_date = self.parse_date(listing_date, "%b-%y")

                    now = datetime.utcnow()
                    last_updated_date = now
                    created_date = now
                    symbol_pair = (ticker, exchange)

                    if symbol_pair not in existing_symbols:
                        symbol = Symbol(
                            exchange_code=exchange,
                            ticker=ticker,
                            instrument=instrument,
                            name=name,
                            sector=sector,
                            currency=currency,
                            mer=mer,
                            benchmark=benchmark,
                            listing_date=listing_date,
                            created_date=created_date,
                            last_updated_date=last_updated_date,
                        )
                        self.symbols.append(symbol)

                        existing_symbols.append(symbol_pair)
