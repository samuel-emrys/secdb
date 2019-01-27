class Price:
    def __init__(
        self,
        vendor,
        symbol,
        price_date,
        created_date,
        last_updated_date,
        open_price=None,
        high_price=None,
        low_price=None,
        close_price=None,
        adj_close_price=None,
        volume=None,
    ):

        self.vendor = vendor
        self.symbol = symbol
        self.price_date = price_date
        self.created_date = created_date
        self.last_updated_date = last_updated_date
        self.open_price = open_price
        self.high_price = high_price
        self.low_price = low_price
        self.close_price = close_price
        self.adj_close_price = adj_close_price
        self.volume = volume

    def __str__(self):
        out = [
            self.vendor,
            self.symbol,
            self.price_date,
            self.created_date,
            self.last_updated_date,
            self.open_price,
            self.high_price,
            self.low_price,
            self.close_price,
            self.adj_close_price,
            self.volume,
        ]
        return ",".join(out)
