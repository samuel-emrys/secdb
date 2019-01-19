class Exchange:
	def __init__(self, abbrev, suffix=None, name=None, city=None, country=None, timezone=None, timezone_offset=None, open_utc=None, close_utc=None):
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

		return (str(self.abbrev) + "," + str(self.suffix) + "," + str(self.name) + "," +
			str(self.city) + "," + str(self.country) + "," + str(self.timezone) + "," +
			str(self.timezone_offset) + "," + str(self.open_utc) + "," + str(self.close_utc))


