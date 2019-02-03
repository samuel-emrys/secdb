from secdb.utils.webio import WebIO
from secdb.vendors.vendor import Vendor
import xml.etree.ElementTree as ET

from secdb.currency import Currency


class CurrencyISO(Vendor):
    def __init__(self, name, website_url, support_email, api):
        super(CurrencyISO, self).__init__(
            name, website_url, support_email, api
        )
        self.file = "list_one.xml"
        self.currencies = []

    def build_prices(self, symbols):
        pass

    def build_currency(self):
        # Scrape ISO 4217 Currency information

        download = WebIO.download(url=self.api.get('url', None), file=self.file)
        download = download.decode("utf-8")

        root = ET.fromstring(download)

        currency_dict = dict()

        # XML is ordered by country, so loop through countries
        for country in root.find("CcyTbl").findall("CcyNtry"):
            currencyName = self.parseCurrencyName(country.find("CcyNm").text)
            try:
                currencyAbbr = self.parseCurrencyAbbr(country.find("Ccy").text)
                currencyNum = country.find("CcyNbr").text
                currencyMinorUnit = self.parseMinorUnit(
                    country.find("CcyMnrUnts").text
                )
                currency_dict[currencyAbbr] = (
                    currency_dict.get(currencyAbbr, 0) + 1
                )

            except AttributeError:
                currencyAbbr = None
                currencyNum = None
                currencyMinorUnit = None

                # Currency has a primary key, and isn't a duplicate entry
            if currencyAbbr is not None and currency_dict[currencyAbbr] == 1:
                currency = Currency(
                    currencyAbbr, currencyNum, currencyName, currencyMinorUnit
                )
                self.currencies.append(currency)

        return self.currencies

    def build_exchanges(self):
        pass

    def build_symbols(self, currencies, exchanges):
        pass

    def parseMinorUnit(self, currency_minor_unit):
        try:
            int(currency_minor_unit)
            return currency_minor_unit
        except ValueError:
            return 0

    def parseCountryName(self, country_name):
        return country_name

    def parseCurrencyName(self, currency_name):
        return currency_name

    def parseCurrencyAbbr(self, currency_abbr):
        return currency_abbr
