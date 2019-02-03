from datetime import datetime
from lxml import html
from secdb.utils.webio import WebIO
from secdb.vendors.vendor import Vendor
from secdb.exchange import Exchange
from secdb.currency import Currency
from secdb.symbol import Symbol
from secdb.price import Price


class MarketIndex(Vendor):
    def __init__(self, name, website_url, support_email, api):
        super(MarketIndex, self).__init__(
            name, website_url, support_email, api
        )
        self.prices = {}

    def build_prices(self, symbols):
        self.exchange = "ASX"

        price_page = WebIO.download(self.api_url).decode("utf-8")
        price_tree = html.fromstring(price_page)

        div = price_tree.xpath('//div[@class="header-timestamp"]')[0]
        time_phrase = div.text_content()
        date_str = time_phrase.replace("At the close on ", "")
        date = self.parse_date(date_str, "%d %b %Y")

        table = price_tree.xpath('//table[@id="asx_sp_table"]')[0]
        rows = table.xpath("./tbody/tr")

        for row in rows:
            ticker = self.parseTicker(row[2].text_content())
            price = self.parse_price(row[4].text_content())

            now = datetime.utcnow()
            priceObj = Price(
                price_date=date,
                symbol=ticker,
                close_price=price,
                vendor=self,
                created_date=now,
                last_updated_date=now,
            )
            key = (ticker, self.exchange)
            self.prices[key] = priceObj

        return self.prices

    def build_currency(self):
        pass

    def build_exchanges(self):
        pass

    def build_symbols(self, currencies, exchanges):
        pass
