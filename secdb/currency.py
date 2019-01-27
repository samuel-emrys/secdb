class Currency:
    def __init__(self, abbrev, num=None, name=None, minor_unit=None):
        self.abbrev = abbrev
        self.num = num
        self.name = name
        self.minor_unit = minor_unit

    def __str__(self):

        out = [
            self.abbrev,
            self.num,
            self.name,
            self.minor_unit,
        ]
        return ",".join(out)
