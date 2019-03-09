from secdb.vendors.vendor import Vendor
from secdb.utils.webio import WebIO
import json
import logging
from datetime import datetime
from secdb.price import Price


class IEX(Vendor):
    def __init__(self, name, website_url, support_email, api):
        super(IEX, self).__init__(
            name, website_url, support_email, api
        )
        self.api_url = "https://api.iextrading.com/1.0/stock/SYMBOL/chart/5y"
        # Build methods

    def build_symbols(self, currencies, exchanges):
        # scrape https://iextrading.com/trading/eligible-symbols/
        pass

    def build_prices(self, symbols):
        """
            [
            {
                "date":"2014-01-28",
                "open":66.7037,
                "high":67.5219,
                "low":65.8266,
                "close":66.4074,
                "volume":266833581,
                "unadjustedVolume":38119083,
                "change":-5.7689,
                "changePercent":-7.993,
                "vwap":66.7869,
                "label":"Jan 28, 14",
                "changeOverTime":0
            },
        """
        for symbol_key in symbols:
            symbol = symbols[symbol_key]

            try:
                query = (
                    self.api['url']
                    + "/stock/"
                    + symbol.ticker
                    + "/chart/5y"
                )
            except KeyError:
                logging.debug("IEX API url not provided")

            download = WebIO.download(query).decode("utf-8")

            if (
                ("Unknown symbol" not in download)
                and (download is not None)
            ):
                json_prices = json.loads(download)

                for price_dict in json_prices:
                    now = datetime.utcnow()
                    date_str = price_dict.get("date", None)
                    price_date = self.parse_date(date_str, "%Y-%m-%d")
                    ticker = symbol.ticker
                    open_price = price_dict.get("open", None)
                    high_price = price_dict.get("high", None)
                    low_price = price_dict.get("low", None)
                    close_price = price_dict.get("close", None)
                    volume = price_dict.get("volume", None)

                    if price_date is not None:
                        price = Price(
                            vendor=IEX,
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
                        # print(price)

                        self.prices.append(price)

                        if (len(self.prices) == 100):
                            # Add price list to database
                            self.session.bulk_save_objects(self.prices)
                            self.session.commit()
                            # flush price list
                            self.prices = []

                    # Add the remaining prices to database
                    self.session.bulk_save_objects(self.prices)
                    self.session.commit()
                    # flush price list
                    self.prices = []

    def build_currency(self):
        pass

    def build_exchanges(self):
        pass

        # Update methods

    def update_symbols(self):
        pass

    def update_prices(self):
        pass

    def update_currency(self):
        pass

    def update_exchanges(self):
        pass


if __name__ == "__main__":
    json_filename = "../tests/aapl-iex.json"
    with open(json_filename) as json_data_file:
        symbols = json.load(json_data_file)

    vendor = IEX("IEX", "iex.com", "test@test", "api")
    vendor.build_prices(symbols)
