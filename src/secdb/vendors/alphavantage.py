from secdb.vendors.vendor import Vendor


class AlphaVantage(Vendor):
    def __init__(self, name, website_url, support_email, api):
        super(AlphaVantage, self).__init__(
            name, website_url, support_email, api
        )
        # Build methods

    def build_symbols(self, currencies, exchanges):
        pass

    def build_prices(self):
        pass

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
