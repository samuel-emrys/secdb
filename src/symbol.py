
class Symbol:
	def __init__(exchange_code, ticker, instrument, name, sector, currency, mer,
	 	benchmark, listing_date, created_date, last_updated_date):
	
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
		return self.exchange_code + "," + self.ticker + "," + self.instrument + "," +
			self.name + "," + self.sector + "," + self.currency + "," + self.mer + 
			"," + self.benchmark + "," + self.listing_date + "," + self.created_date +
			"," + self.last_updated_date




