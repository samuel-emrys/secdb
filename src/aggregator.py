from exchange import Exchange
from currency import Currency
from symbol import Symbol

class Aggregator:
	'''
	This class is the authoritative source of all data. This class will parse the data and 
	aggregate it into one set, ensuring that there are no errors or duplicates, and it is as 
	complete as possible
	'''
	def __init__(self):
		self.currencies = {}
		self.symbols = {}
		self.exchanges = {}
		self.prices = {}

	def import_currencies(self, currencies):

		currencies = [x for x in currencies if x is not None]

		if len(currencies) == 1:
			for source in currencies:
				for currency in source:
					self.currencies[currency.abbrev] = currency
		else:
			# Currency-ISO is not the only vendor, handle this appropriately
			pass

	def import_symbols(self, symbols):
		symbols = [x for x in symbols if x is not None]

		for source in symbols:
			for symbol in source:
				key = (symbol.ticker, symbol.exchange_code)
				if key not in self.symbols:
					self.symbols[key] = symbol

		for key in self.symbols:
			print(self.symbols[key])


	def import_exchanges(self, exchanges):
		
		exchanges = [x for x in exchanges if x is not None]

		for source in exchanges:
			for exchange in source:
				if exchange.abbrev not in self.exchanges:
					self.exchanges[exchange.abbrev] = exchange

	def import_prices(self, prices):
		pass