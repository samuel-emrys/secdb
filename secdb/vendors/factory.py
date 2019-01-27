import utils.helpers as helpers
import logging
from datetime import datetime
from vendors.vendor import Vendor
from vendors.asx import VendorASX
from vendors.asxh import VendorASXHistorical
from vendors.currencyiso import VendorCurrencyISO
from vendors.marketindex import VendorMarketIndex
from vendors.worldtradingdata import VendorWorldTradingData
from vendors.alphavantage import VendorAlphaVantage
from vendors.barchart import VendorBarchart
from vendors.iex import VendorIEX
from vendors.stooq import VendorStooq
from vendors.qandl import VendorQandl


class VendorFactory:
    def __init__(self):
        self.factory = {
            "asx": VendorASX,
            "alphavantage": VendorAlphaVantage,
            "qandl": VendorQandl,
            "worldtradingdata": VendorWorldTradingData,
            "barchart": VendorBarchart,
            "stooq": VendorStooq,
            "iex": VendorIEX,
            "asxhistoricaldata": VendorASXHistorical,
            "marketindex": VendorMarketIndex,
            "currencyiso": VendorCurrencyISO,
        }

    def __call__(self, vendor_name, config):
        name = self._parse_config(config.get(vendor_name, "name"))
        website_url = self._parse_config(
            config.get(vendor_name, "website_url")
        )
        support_email = self._parse_config(
            config.get(vendor_name, "support_email")
        )
        api_url = self._parse_config(config.get(vendor_name, "api_url"))
        api_key = self._parse_config(config.get(vendor_name, "api_key"))
        now = datetime.utcnow()
        try:
            obj = self.factory[vendor_name.lower()](
                name, website_url, support_email, api_url, api_key
            )
            return obj

        except Exception:
            out = "%s: Vendor '%s' not currently supported. Skipping" % (
                str(now),
                name
                )
            logging.info(out)

    def _parse_config(self, element):
        element = helpers.removeWhitespace(element)
        if element == "NA" or element == "":
            return None

        return element
