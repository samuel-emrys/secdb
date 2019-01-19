class Currency:
	def __init__(self, abbrev, num=None, name=None, minor_unit=None):
		self.abbrev = abbrev
		self.num = num
		self.name = name
		self.minor_unit = minor_unit

	def __str__(self):

		return (str(self.abbrev) + "," + str(self.num) + "," + str(self.name) + "," +
			str(self.minor_unit))