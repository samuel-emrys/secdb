import utils.helpers as helpers
import logging
import requests
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

        api = config[vendor_name].get('api', None)
        name = config[vendor_name].get('name', None)
        website_url = config[vendor_name].get('website_url', None)
        support_email = config[vendor_name].get('support_email', None)
        now = datetime.utcnow()

        try:
            obj = self.factory[vendor_name.lower()](
                name, website_url, support_email, api
            )
            return obj

        except Exception:
            out = "%s: Vendor '%s' not currently supported. Skipping" % (
                str(now),
                name
                )
            logging.info(out)
