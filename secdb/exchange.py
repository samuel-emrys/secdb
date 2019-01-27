class Exchange:
    def __init__(
        self,
        abbrev,
        suffix=None,
        name=None,
        city=None,
        country=None,
        timezone=None,
        timezone_offset=None,
        open_utc=None,
        close_utc=None,
    ):
        self.abbrev = abbrev
        self.suffix = suffix
        self.name = name
        self.city = city
        self.country = country
        self.timezone = timezone
        self.timezone_offset = timezone_offset
        self.open_utc = open_utc
        self.close_utc = close_utc

    def __str__(self):

        out = [
            self.abbrev,
            self.suffix,
            self.name,
            self.city,
            self.country,
            self.timezone,
            self.timezone_offset,
            self.open_utc,
            self.close_utc
        ]
        return ",".join(out)
