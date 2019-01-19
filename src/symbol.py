
class Symbol:
	def __init__(self, exchange_code, ticker, created_date, last_updated_date, instrument=None, name=None, sector=None, currency=None, mer=None,
	 	benchmark=None, listing_date=None):
	
		self.exchange_code = exchange_code
		self.ticker = ticker
		self.instrument = instrument
		self.name = name
		self.sector = sector
		self.currency = currency
		self.mer = mer
		self.benchmark = benchmark
		self.listing_date = listing_date
		self.created_date = created_date
		self.last_updated_date = last_updated_date

	def __str__(self):
		return (str(self.exchange_code) + "," + str(self.ticker) + "," + str(self.instrument) + "," +
			str(self.name) + "," + str(self.sector) + "," + str(self.currency) + "," + str(self.mer) + 
			"," + str(self.benchmark) + "," + str(self.listing_date) + "," + str(self.created_date) +
			"," + str(self.last_updated_date))




