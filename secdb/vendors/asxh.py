import zipfile
import sys
import io
import utils.helpers as helpers

from datetime import datetime
from utils.webio import WebIO
from vendors.vendor import Vendor
from lxml import html
from exchange import Exchange
from currency import Currency
from symbol import Symbol
from price import Price


class VendorASXHistorical(Vendor):
    """
        @TODO:
            Pull Historical ASX Symbols
            - Try to find whether these have been delisted or not, and create
            links with symbols that changed names
    """

    def __init__(self, name, website_url, support_email, api_url, api_key):
        super(VendorASXHistorical, self).__init__(
            name, website_url, support_email, api_url, api_key
        )
        self.archive_url = "https://www.asxhistoricaldata.com/archive/"
        self.file_list = self.build_file_list()
        self.zip_list = {}

        self.exchange = "ASX"
        self.currency = "AUD"
        self.symbols = []
        self.prices = []

    def build_price(self, symbols):
        for zip_name in self.zip_list:
            sys.stderr.write("\n")

            count = 0
            for file_name in self.zip_list[zip_name].namelist():
                count += 1
                file = self.zip_list[zip_name].open(file_name, "r")
                sys.stderr.write(
                    "\rParsing file [%s/%s] in %s"
                    % (
                        count,
                        len(self.zip_list[zip_name].namelist()),
                        zip_name,
                    )
                )
                sys.stderr.flush()

                file_name_str = file_name.split(".")[0].split("/")[1]
                date = self.parse_date(file_name_str, "%Y%m%d")

                # Ticker, Date, Open, High, Low, Close, Volume.
                for line in file:
                    line_elements = line.decode().split(",")
                    ticker = line_elements[0]
                    open_price = line_elements[2]
                    high_price = line_elements[3]
                    low_price = line_elements[4]
                    close_price = line_elements[5]
                    volume = line_elements[6]
                    now = datetime.utcnow()

                    if date is not None:
                        price = Price(
                            price_date=date,
                            vendor=VendorASXHistorical,
                            symbol=ticker,
                            open_price=open_price,
                            high_price=high_price,
                            low_price=low_price,
                            close_price=close_price,
                            volume=volume,
                            created_date=now,
                            last_updated_date=now,
                        )

                        self.prices.append(price)
                        # TODO: Insert self.prices to database, too large to
                        # append outside this.

    def build_currency(self):
        pass

    def build_exchanges(self):
        pass

    def build_symbols(self, currencies, exchanges):
        self.currencies = currencies

        symbol_count = {}

        for f in self.file_list:

            download = WebIO.download(url=self.api_url, file=f)

            z = zipfile.ZipFile(io.BytesIO(download))

            self.zip_list[f] = z

            # Iterate through files in zip file
            count = 0
            for file_name in z.namelist():
                count += 1
                file = z.open(file_name, "r")

                sys.stderr.write(
                    "\rParsing file [%s/%s] in %s"
                    % (count, len(z.namelist()), f)
                )
                sys.stderr.flush()
                # Get first element from each line (this is the symbol)
                for line in file:
                    lineElements = line.decode().split(",")
                    ticker = lineElements[0]
                    symbol_count[ticker] = symbol_count.get(ticker, 0) + 1
                    # Make sure symbol is unique before adding to list
                    # if ticker not in symbols:
                    if symbol_count[ticker] == 1:
                        now = datetime.utcnow()
                        last_updated_date = now
                        created_date = now

                        symbol = Symbol(
                            exchange_code=self.exchange,
                            ticker=ticker,
                            currency=self.currency,
                            created_date=created_date,
                            last_updated_date=last_updated_date,
                        )
                        self.symbols.append(symbol)

        return self.symbols

    def build_file_list(self):
        file_list = []

        # TODO: Implement custom print message parameter for WebIO.download
        # function
        historical_page = WebIO.download(self.archive_url).decode("utf-8")
        historical_tree = html.fromstring(historical_page)

        recent_page = WebIO.download(self.website_url).decode("utf-8")
        recent_tree = html.fromstring(recent_page)

        ha_elements = historical_tree.xpath("//a")
        ra_elements = recent_tree.xpath("//a")

        a_elements = ha_elements + ra_elements

        for a in a_elements:
            link = a.attrib["href"]
            if ".zip" in link:
                file = link.split("/")[-1]
                file_list.append(file)

        return file_list
