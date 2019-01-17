class Exchange:
	def __init__(abbrev, suffix, name, city, country, timezone, timezone_offset, open_time, close_time):
		self.abbrev = abbrev
		self.suffix = suffix
		self.name = name
		self.city = city
		self.country = country
		self.timezone = timezone
		self.timezone_offset = timezone_offset
		self.open_time = open_time
		self.close_time = close_time

	def __str__(self):
		return self.abbrev + "," + self.suffix + "," + self.name + "," +
			self.city + "," + self.country + "," + self.timezone + "," +
			self.timezone_offset + "," + self.open_time + "," + self.close_time


