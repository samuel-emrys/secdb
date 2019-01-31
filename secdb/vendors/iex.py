from vendors.vendor import Vendor
from utils.webio import WebIO
import json
from datetime import datetime
from price import Price


class VendorIEX(Vendor):
    def __init__(self, name, website_url, support_email, api):
        super(VendorIEX, self).__init__(
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
        for symbol in symbols:
            query = self.api_url.replace("SYMBOL", symbol.ticker)

            download = WebIO.download(query).decode("utf-8")
            json_prices = json.loads(download)

            if (
                ("Unknown symbol" not in download)
                and (download is not None)
            ):
                for field in json_prices:
                    for price_dict in json_prices[field]:
                        now = datetime.utcnow()
                        # This date needs to have timezone information.
                        # currently being truncated in conversion
                        date_str = price_dict["date"]
                        price_date = self.parse_date(date_str, "%Y-%m-%d")
                        ticker = symbol.ticker
                        open_price = price_dict["open"]
                        high_price = price_dict["high"]
                        low_price = price_dict["low"]
                        close_price = price_dict["close"]
                        volume = price_dict["volume"]

                        if price_date is not None:
                            price = Price(
                                vendor=VendorIEX,
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
