from webio import WebIO
from abc import abstractmethod
from datetime import datetime
from datetime import timedelta
from lxml import html

import configparser
import helpers
import logging
import string
import requests
import csv
import io
import re
import zipfile
import sys
import xml.etree.ElementTree as ET

from exchange import Exchange
from currency import Currency
from symbol import Symbol


class Vendor:
	# Abstract vendor class, individual vendors inherit from this

	# Constructor
	def __init__(self, name, website_url, support_email, api_url, api_key):
		self.name = name
		self.website_url = website_url
		self.support_email = support_email
		self.api_url = api_url
		self.api_key = api_key

	# String cast overload
	def __str__(self):

		return (str(self.name) + "," + str(self.website_url) + "," + 
			str(self.support_email) + "," + str(self.api_url) + "," + str(self.api_key))

	# Symbol Helper methods
	def parse_vendor(element):
		element = helpers.removeWhitespace(element)

		if (element == 'NA' or element == ''):
			return None

		return element

	def parseTicker(self, ticker):
		# Remove extraneous white space from left and right of string, and remove tabs/new line characters from middle of string
		ticker = ticker.strip().translate( { ord(c):None for c in '\n\t\r' } )

		# Could also check that it contains only uppercase characters, length 3-5 (what's the maximum ticker length?)
		return ticker

	def parseInstrument(self, instrument):
		# Remove extraneous white space from left and right of string, and remove tabs/new line characters from middle of string
		instrument = instrument.strip().translate( { ord(c):None for c in '\n\t\r' } )

		return instrument

	def parseName(self, name):
		# Remove extraneous white space from left and right of string, and remove tabs/new line characters from middle of string
		name = name.strip().translate( { ord(c):None for c in '\n\t\r' } )

		return name

	def parseSector(self, sector):
		if (sector != None):
			# Remove extraneous white space from left and right of string, and remove tabs/new line characters from middle of string
			sector = sector.strip().translate( { ord(c):None for c in '\n\t\r' } )

			if (sector == "#" or sector == "Not Applic"):
				sector = None

		return sector

	def parseCurrency(self, currency):
		# cursor = con.cursor()
		# query = "SELECT code FROM CURRENCY;"
		# cursor.execute(query)
		# cursorOutput = cursor.fetchall()
		# currencyList = [x[0] for x in cursorOutput]

		# if (currency not in currencyList):
		# 	currency = None

		return currency

	def parseMER(self, mer):
		if (mer != None):
			# Remove extraneous white space from left and right of string, and remove tabs/new line characters from middle of string
			mer = mer.strip().translate( { ord(c):None for c in '\n\t\r' } )

			if (mer == "-"):
				mer = None
			# else if string doesn't match a decimal
			elif not (re.match(r"^[0-9]{1,2}(.[0-9]+?)?$", mer)):
				now = datetime.utcnow()
				logging.debug(str(now) + " Invalid MER ' " + mer + "' identified. Sanitized with 'None'.")
				mer = None

		return mer

	def parseBenchmark(self, benchmark):
		if (benchmark != None):
			# Remove extraneous white space from left and right of string, and remove tabs/new line characters from middle of string
			benchmark = benchmark.strip().translate( { ord(c):None for c in '\n\t\r' } )

			if (benchmark == "-"):
				benchmark = None

		return benchmark

	def parseListingDate(self, listingDate, dateFormat):
		
		# Remove extraneous white space from left and right of string, and remove tabs/new line characters from middle of string
		listingDateString = listingDate.strip().translate( { ord(c):None for c in '\n\t\r' } )

		try:
			listingDate = datetime.strptime(listingDateString, dateFormat)

		except ValueError:
			listingDate = None

		return listingDate


	# Exchange Helper Methods
	# @TODO: Put these in Exchange class, refactor method of parsing
	# Actually, maybe I should make a vendor for wikipedia... content scraped from wikipedia should be parsed by the grabbing object
	def parseName(self, name):
		name = helpers.removeWhitespace(name)
		name = helpers.removeWikipediaReferences(name)

		return name

	def parseAbbr(self, abbr):
		abbr = helpers.removeWhitespace(abbr)
		abbr = helpers.removeWikipediaReferences(abbr)

		# abbr = re.sub(r"\[.*\]","", abbr)
		return abbr

	def parseCountry(self, country):
		country = helpers.removeWhitespace(country)
		country = helpers.removeWikipediaReferences(country)
		# country = re.sub(r"\[.*\]","", country)
		return country

	def parseCity(self, city):
		city = helpers.removeWhitespace(city)
		city = helpers.removeWikipediaReferences(city)
		# city = re.sub(r"\[.*\]","", city)
		return city

	def parseTimezone(self, timezone):
		timezone = helpers.removeWhitespace(timezone)
		timezone = helpers.removeWikipediaReferences(timezone)
		# timezone = re.sub(r"\[.*\]","", timezone)
		return timezone

	def parseTZOffset(self, delta):
		delta = helpers.removeWhitespace(delta)
		delta = helpers.removeWikipediaReferences(delta)
		delta = delta.replace("−", "-"); 
		# delta = re.sub(r"\[.*\]","", delta)
		delta = timedelta(hours=float(delta))

		return delta

	def parseDST(self, dst):
		dst = helpers.removeWhitespace(dst)
		dst = helpers.removeWikipediaReferences(dst)
		# dst = re.sub(r"\[.*\]","", dst)
		return dst

	def parseTime(self, time):
		time = helpers.removeWhitespace(time)
		time = helpers.removeWikipediaReferences(time)
		# time = re.sub(r"\[.*\]","", time)
		time = datetime.strptime(time,"%H:%M").time()

		return time

	# Factory to generate appropriate subclass
	def factory(title, config):
		name = Vendor.parse_vendor(config.get(title, 'name'))
		website_url = Vendor.parse_vendor(config.get(title, 'website_url'))
		support_email = Vendor.parse_vendor(config.get(title, 'support_email'))
		api_url = Vendor.parse_vendor(config.get(title, 'api_url'))
		api_key = Vendor.parse_vendor(config.get(title, 'api_key'))
		now = datetime.utcnow()

		if title == 'asx': 
			return VendorASX(name, website_url, support_email, api_url, api_key)
		elif title == 'alphavantage': 
			logging.info(str(now) + ": Vendor '"+name+"' not currently supported. Skipping")
		elif title == 'quandl': 
			logging.info(str(now) + ": Vendor '"+name+"' not currently supported. Skipping")
		elif title == 'worldtradingdata': 
			return VendorWorldTradingData(name, website_url, support_email, api_url, api_key)
		elif title == 'barchart': 
			logging.info(str(now) + ": Vendor '"+name+"' not currently supported. Skipping")
		elif title == 'stooq': 
			logging.info(str(now) + ": Vendor '"+name+"' not currently supported. Skipping")
		elif title == 'iex': 
			logging.info(str(now) + ": Vendor '"+name+"' not currently supported. Skipping")
		elif title == 'asxhistoricaldata': 
			return VendorASXHistorical(name, website_url, support_email, api_url, api_key)
		elif title == 'marketindex': 
			logging.info(str(now) + ": Vendor '"+name+"' not currently supported. Skipping")
		elif title == 'currencyiso':
			return VendorCurrencyISO(name, website_url, support_email, api_url, api_key)
		else:
			logging.info(str(now) + ": Vendor '"+name+"' not currently supported. Skipping")


	factory = staticmethod(factory)


	# Build methods
	@abstractmethod
	def build_symbols(self):
		pass

	@abstractmethod
	def build_prices(self):
		pass

	@abstractmethod
	def build_currency(self):
		pass

	@abstractmethod
	def build_exchanges(self):
		pass

	# Update methods
	@abstractmethod
	def update_symbols(self):
		pass

	@abstractmethod
	def update_prices(self):
		pass

	@abstractmethod
	def update_currency(self):
		pass

	@abstractmethod
	def update_exchanges(self):
		pass



class VendorASX(Vendor):
	def __init__(self, name, website_url, support_email, api_url, api_key):
		super(VendorASX, self).__init__(name, website_url, support_email, api_url, api_key)
		self.company_url = 'https://www.asx.com.au/asx/research/'
		self.company_file = 'ASXListedCompanies.csv'
		self.etp_url = 'https://www.asx.com.au/products/etf/managed-funds-etp-product-list.htm'
		self.symbols = []


	def build_currency(self):
		pass

	def build_price(self):
		pass

	def build_exchanges(self):
		pass

	def build_symbols(self):
		## Scrape https://www.marketindex.com.au/asx-listed-companies to confirm list complete

		self.build_companies()
		self.build_exchange_products()

		return self.symbols

	def build_companies(self):

		# response = requests.get(self.company_url)
		download = WebIO.download(url=self.company_url, file=self.company_file)
		download = download.decode('utf-8')
		csvfile = io.StringIO(download, newline='')
		companies = csv.reader(csvfile)

		instrument = 'Shares'
		currency = 'AUD'
		exchange = 'ASX'
		MER = None
		benchmark = None
		existing_symbols = [(x.ticker, x.exchange_code) for x in self.symbols]

		count = 0
		for company in companies:
			count+=1; #counts the number of lines before entries should be entered (truncates first 3 lines)

			if (len(company) > 0 and count > 3):
				ticker = None;
				name = company[0];
				sector = None;
				if (len(company) == 2):
					ticker = company[1];
				elif (len(company) == 3):
					ticker = company[1];
					sector = company[2];

				# Create a tuple in DB format and append to total list.
				# Need to add query to DB to check if ticker already exists. If it doesn't, add "now" as created date, otherwise leave no entry for this
				
				sector = self.parseSector(sector)

				now = datetime.utcnow()
				created_date = now
				last_updated_date = now	

				symbol_pair = (ticker, exchange)
				if (symbol_pair not in existing_symbols):
					symbol = Symbol(exchange_code=exchange, ticker=ticker, instrument=instrument, 
						name=name, sector=sector, currency=currency, mer=MER, benchmark=benchmark, 
						created_date=created_date, last_updated_date=last_updated_date)
					self.symbols.append(symbol)
					# self.symbols.append( (exchange, ticker, instrument, name, sector, currency, MER, benchmark, None, created_date, last_updated_date) );
					existing_symbols.append(symbol_pair)

		# return self.symbols

	def build_exchange_products(self):

		page = requests.get(self.etp_url)

		tree = html.fromstring(page.content)
		tr_elements = tree.xpath('//tr')

		# Initialise table entry values
		table_format = ""
		sector = None
		currency = 'AUD'
		exchange = 'ASX'
		existing_symbols = [(x.ticker, x.exchange_code) for x in self.symbols]

		for row in tr_elements:
			first_element = helpers.removeWhitespace(row[0].text_content())

			# Identify which table is being parsed and define table format
			if (first_element == "Exposure"):
				if (len(row) == 9):
					table_format = "LIC"
				elif (len(row) == 6):
					table_format = "AREITS"
				elif (len(row) == 10 and helpers.removeWhitespace(row[3].text_content()) == "iNAV Code"):
					table_format = "ETP"
				else:
					table_format = "ETP_SINGLE_ASSET"

			elif (first_element == "Name"):
				if (len(row) == 7):
					table_format = "INFRASTRUCTURE"
				elif (len(row) == 8):
					table_format = "ABS_RETURN_FUNDS"
				elif (len(row) == 6):
					table_format = "PDFs"

			# Store the row contents based on the identified table format
			else:
				if (len(row) == 1):
					# Sector is on its own line, so parse length 1 lines to obtain sector for following entries
					sector 			= row[0].text_content()
				
				elif (table_format == "LIC"):

					name 			= row[0].text_content()
					ticker 			= row[1].text_content()
					instrument 		= row[2].text_content()
					benchmark 		= row[3].text_content()
					mer 			= row[4].text_content()
					listing_date 	= row[6].text_content()

				elif (table_format == "AREITS"):

					name 			= row[0].text_content()
					ticker 			= row[1].text_content()
					instrument 		= row[2].text_content()
					benchmark 		= None
					mer 			= None
					listing_date 	= row[3].text_content()

				elif (table_format == "ETP"):

					name 			= row[0].text_content()
					ticker 			= row[1].text_content()
					instrument 		= row[2].text_content()
					benchmark 		= row[4].text_content()
					mer 			= row[6].text_content()
					listing_date 	= row[7].text_content()

				elif (table_format == "ETP_SINGLE_ASSET"):

					name 			= row[0].text_content()
					ticker 			= row[1].text_content()
					instrument 		= row[2].text_content()
					benchmark 		= row[4].text_content()
					mer 			= row[6].text_content()
					listing_date 	= row[7].text_content()

				elif (table_format == "INFRASTRUCTURE"):
					name 			= row[0].text_content()
					ticker 			= row[1].text_content()
					instrument 		= row[2].text_content()
					sector 			= row[3].text_content()
					benchmark 		= None
					mer 			= None
					listing_date 	= row[4].text_content()

				elif (table_format == "ABS_RETURN_FUNDS"):

					name 			= row[0].text_content()
					ticker 			= row[1].text_content()
					instrument 		= row[2].text_content()
					sector 			= None
					benchmark 		= row[3].text_content()
					mer 			= row[4].text_content()
					listing_date 	= row[5].text_content()

				elif (table_format == "PDFs"):
					name 			= row[0].text_content()
					ticker 			= row[1].text_content()
					instrument 		= row[2].text_content()
					sector 			= None
					benchmark 		= None
					mer 			= None
					listing_date 	= row[3].text_content()


				if (len(row) > 1):

					ticker 			= self.parseTicker(ticker)
					instrument 		= self.parseInstrument(instrument)
					name 			= self.parseName(name)
					sector 			= self.parseSector(sector)
					currency 		= self.parseCurrency(currency)
					mer 			= self.parseMER(mer)
					benchmark 		= self.parseBenchmark(benchmark)
					listing_date 	= self.parseListingDate(listing_date, '%b-%y')

					#print("%s | %s | %s | %s | %s | %s | %s | %s" % (name, ticker, instrument, sector, benchmark, MER, opFee, listingDate))
					now 			= datetime.utcnow()
					last_updated_date = now
					created_date 	= now


					symbol_pair = (ticker, exchange)
					if (symbol_pair not in existing_symbols):
						symbol = Symbol(exchange_code=exchange, ticker=ticker, instrument=instrument, 
							name=name, sector=sector, currency=currency, mer=mer, benchmark=benchmark, 
							listing_date=listing_date, created_date=created_date, last_updated_date=last_updated_date)
						self.symbols.append(symbol)

						# self.symbols.append( (exchange, ticker, instrument, name, sector, currency, mer, benchmark, listing_date, created_date, last_updated_date) );
						existing_symbols.append(symbol_pair)

		# return self.symbols

class VendorWorldTradingData(Vendor):
	def __init__(self, name, website_url, support_email, api_url, api_key):
		super(VendorWorldTradingData, self).__init__(name, website_url, support_email, api_url, api_key)
		self.stock_url = "https://www.worldtradingdata.com/download/list"
		self.login_url = "https://www.worldtradingdata.com/login"
		self.symbols = []
		self.exchanges = []

	def build_price(self):
		pass

	def build_currency(self):
		pass

	def build_symbols(self):


		# session = requests.Session() # create a requests Session
		# r = session.get(self.login_url)

		# ### Get token
		# tree = html.fromstring(r.content)
		# token_value = tree.xpath('//input[@name="_token"]/@value')
		# token = str(token_value[0])
		# # Form credentials
		# cred_filename = 'credentials.conf'
		
		# # Load Configuration File
		# credentials = configparser.RawConfigParser()
		# credentials.read(cred_filename)

		# for cred in credentials.sections():
		# 	email = credentials.get(cred, 'user')
		# 	password = credentials.get(cred, 'password')

		# # Create credentials dictionary
		# data_credentials = {'email': email, 'password': password, '_token': token}

		# # Log in to requests session, send post
		# r2 = session.post(login_url, data=data_credentials)
		session = WebIO.login(self.login_url)
		download = WebIO.download(url=self.stock_url,session=session)

		# response = session.get(stockListURL, timeout=(15,15))
		# csvfile = io.StringIO(download.text, newline='')
		csvfile = io.StringIO(download.decode('utf-8'))
		stocklist = csv.reader(csvfile)

		# Get list of abbreviations in exchange list
		# cursor = con.cursor()
		# query = "SELECT abbrev FROM EXCHANGE;"
		# cursor.execute(query)
		# cursor_out = cursor.fetchall()
		# exchange_list = [x[0] for x in cursor_out]
		existing_symbols = [(x[1], x[0]) for x in self.symbols]


		# Parse symbols in the stocklist, and add them to list for addition to database
		for line in stocklist:

			exchange = helpers.removeWhitespace(line[4])
			name = helpers.removeWhitespace(line[1])
			currency = helpers.removeWhitespace(line[2])
			currency = self.parseCurrency(currency)
			symbol_list = line[0].split('.')

			symbol = helpers.removeWhitespace(''.join(symbol_list[:-1])) if len(symbol_list) > 1 else helpers.removeWhitespace(symbol_list[0])

			# print("%s | %s | %s | %s" % (symbol, name, currency, exchange))
			now = datetime.utcnow()
			created_date = now
			last_updated_date = now

			# print(symbol in exchangeList)
			# if (exchange in exchange_list and currency != None):

			symbol_pair = (symbol, exchange)
			if (symbol_pair not in existing_symbols):
				self.symbols.append( (exchange, symbol, None, name, None, currency, None, None, None, created_date, last_updated_date) )
				existing_symbols.append(symbol_pair)

		# return content

	def build_exchanges(self):

		# Login and download file
		session = WebIO.login(self.login_url)
		download = WebIO.download(url=self.stock_url,session=session)

		# Read file as csv in memory
		csvfile = io.StringIO(download.decode('utf-8'))
		stocklist = csv.reader(csvfile)

		# Create map of exchanges to count multiple instances of each
		exchangeCount = {}

		# Create dataset of suffixes
		for line in stocklist:

			exchange = helpers.removeWhitespace(line[4])
			exchangeDesc = helpers.removeWhitespace(line[3])
			suffixList = line[0].split('.')
			suffixToken = helpers.removeWhitespace(suffixList[-1])

			if (suffixToken == 'A' or suffixToken == 'B' or suffixToken == 'C' or suffixToken == 'V' or len(suffixList) == 1):
				suffix = None
			else:
				suffix = suffixToken

			if (exchange != 'N/A') and (not re.match(r"(.*?)INDEX(.*)", exchange)) and (' ' not in exchange):
				exchangeCount[exchange] = exchangeCount.get(exchange, 0) + 1
				if (exchangeCount[exchange] == 1):
					exchangeObj = Exchange(abbrev=exchange, suffix=suffix, name=exchangeDesc)
					self.exchanges.append( exchangeObj )


		print(str(len(self.exchanges)) + " items downloaded")

		self.addTZData()

		return self.exchanges

	def addTZData(self):
		NAME_ELEMENT = 0
		ID_ELEMENT = 1
		COUNTRY_ELEMENT = 2
		CITY_ELEMENT = 3
		ZONE_ELEMENT = 4
		DELTA_ELEMENT = 5
		DST_ELEMENT = 6
		OPEN_LOCAL_ELEMENT = 7
		CLOSE_LOCAL_ELEMENT = 8
		OPEN_UTC_ELEMENT = 10
		CLOSE_UTC_ELEMENT = 11
		DATA_ROW_LENGTH = 13

		exchangeWikiURL = 'https://en.wikipedia.org/wiki/List_of_stock_exchange_trading_hours'
		page = requests.get(exchangeWikiURL)
		tree = html.fromstring(page.content)
		tr_elements = tree.xpath('//tr')
		wiki_exchanges = {}
		# content = []
		for row in tr_elements:

			first_element = helpers.removeWhitespace(row[0].text_content())

			if (len(row) == DATA_ROW_LENGTH and first_element != "Name"):
				name = self.parseName(row[NAME_ELEMENT].text_content())
				abbr = self.parseAbbr(row[ID_ELEMENT].text_content())
				country = self.parseCountry(row[COUNTRY_ELEMENT].text_content())
				city = self.parseCity(row[CITY_ELEMENT].text_content())
				zone = self.parseTimezone(row[ZONE_ELEMENT].text_content())
				delta = self.parseTZOffset(row[DELTA_ELEMENT].text_content())
				dst = self.parseDST(row[DST_ELEMENT].text_content())
				open_local = self.parseTime(row[OPEN_LOCAL_ELEMENT].text_content())
				close_local = self.parseTime(row[CLOSE_LOCAL_ELEMENT].text_content())
				open_utc = self.parseTime(row[OPEN_UTC_ELEMENT].text_content())
				close_utc = self.parseTime(row[CLOSE_UTC_ELEMENT].text_content())

				now = datetime.utcnow()
				created_date = now
				last_updated_date = now

				wiki_exchanges[abbr] = (name, city, country, zone, delta, open_utc, close_utc, created_date, last_updated_date)

		for exchange in self.exchanges:

			exchangeData = wiki_exchanges.get(exchange.abbrev, None)

			if (exchangeData != None):

				exchange.city = exchangeData[1]
				exchange.country = exchangeData[2]
				exchange.zone = exchangeData[3]
				exchange.delta = exchangeData[4]
				exchange.open_utc = exchangeData[5]
				exchange.close_utc = exchangeData[6]

class VendorASXHistorical(Vendor):
	def __init__(self, name, website_url, support_email, api_url, api_key):
		super(VendorASXHistorical, self).__init__(name, website_url, support_email, api_url, api_key)
		self.fileList = ['1997-2006.zip',
					'2007-2012.zip',
					'2013-2016.zip',
					'2017july-december.zip',
					'2017jan-june.zip',
					'2018july-sept.zip',
					'2018jan-june.zip']
		self.exchange = 'ASX'
		self.currency = 'AUD'
		self.symbols = []


	def build_price(self):
		pass

	def build_currency(self):
		pass

	def build_exchanges(self):
		pass

	def build_symbols(self):
		
		symbol_count = {}

		for f in self.fileList:
			# url = self.api_url + f

			download = WebIO.download(url=self.api_url, file=f)



			# sys.stderr.write("\n")
			# sys.stderr.write("Downloading %s from asxhistoricaldata.com" % f)

			# headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:64.0) Gecko/20100101 Firefox/64.0'}
			
			# # Download zip content
			# r = requests.get(url, stream=True, headers=headers)
			# total_length = int(r.headers.get('content-length'))
			# content = []

			# # Show progress bar
			# for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1): 
			# 	if chunk:
			# 		# Append chunk to content list
			# 		content.append(chunk)

			# #Rejoin the zip file so it can be parsed
			# download = b"".join(content)

			z = zipfile.ZipFile(io.BytesIO(download))

			# Iterate through files in zip file
			count = 0
			for fileName in z.namelist():
				count += 1
				file = z.open(fileName, 'r')
				# print("Parsing file %s/%s" % (count, len(z.namelist())))

				sys.stderr.write("\rParsing file [%s/%s] in %s" % (count, len(z.namelist()),f))
				sys.stderr.flush()
				# Get first element from each line (this is the symbol)
				for line in file:
					lineElements = line.decode().split(',')
					ticker = lineElements[0]
					symbol_count[ticker] = symbol_count.get(ticker, 0) + 1
					# Make sure symbol is unique before adding to list
					# if ticker not in symbols:
					if symbol_count[ticker] == 1:
						now 			= datetime.utcnow()
						last_updated_date = now
						created_date 	= now

						self.symbols.append( (self.exchange, ticker, None, None, None, self.currency, None, None, None, created_date, last_updated_date) )

		# return symbols

class VendorMarketIndex(Vendor):
	def __init__(self, name, website_url, support_email, api_url, api_key):
		super(VendorMarketIndex, self).__init__(name, website_url, support_email, api_url, api_key)

class VendorQandl(Vendor):
	def __init__(self, name, website_url, support_email, api_url, api_key):
		super(VendorQandl, self).__init__(name, website_url, support_email, api_url, api_key)

class VendorAlphaVantage(Vendor):
	def __init__(self, name, website_url, support_email, api_url, api_key):
		super(VendorAlphaVantage, self).__init__(name, website_url, support_email, api_url, api_key)

class VendorBarchart(Vendor):
	def __init__(self, name, website_url, support_email, api_url, api_key):
		super(VendorBarchart, self).__init__(name, website_url, support_email, api_url, api_key)

class VendorStooq(Vendor):
	def __init__(self, name, website_url, support_email, api_url, api_key):
		super(VendorStooq, self).__init__(name, website_url, support_email, api_url, api_key)

class VendorIEX(Vendor):
	def __init__(self, name, website_url, support_email, api_url, api_key):
		super(VendorIEX, self).__init__(name, website_url, support_email, api_url, api_key)

class VendorCurrencyISO(Vendor):
	def __init__(self, name, website_url, support_email, api_url, api_key):
		super(VendorCurrencyISO, self).__init__(name, website_url, support_email, api_url, api_key)
		self.file = 'list_one.xml'
		self.currencies = []


	def build_price(self):
		pass

	def build_currency(self):
		# Scrape ISO 4217 Currency information
		download = WebIO.download(url=self.api_url, file=self.file)
		download = download.decode('utf-8')

		root = ET.fromstring(download)
		
		currency_dict = dict()

		# XML is ordered by country, so loop through countries
		for country in root.find('CcyTbl').findall('CcyNtry'):
			currencyName = self.parseCurrencyName(country.find('CcyNm').text)
			try:
				currencyAbbr = self.parseCurrencyAbbr(country.find('Ccy').text)
				currencyNum = country.find('CcyNbr').text
				currencyMinorUnit = self.parseMinorUnit(country.find('CcyMnrUnts').text)
				currency_dict[currencyAbbr] = currency_dict.get(currencyAbbr, 0) + 1

			except AttributeError:
				currencyAbbr = None
				currencyNum = None
				currencyMinorUnit = None

			# Currency has a primary key, and isn't a duplicate entry
			if (currencyAbbr is not None and currency_dict[currencyAbbr] == 1):
				currency = Currency(currencyAbbr, currencyNum, currencyName, currencyMinorUnit)
				self.currencies.append( currency )

		return self.currencies

	def build_exchanges(self):
		pass

	def build_symbols(self):
		pass

	def parseMinorUnit(self, currencyMinorUnit):
		try:
			int(currencyMinorUnit)
			return currencyMinorUnit
		except ValueError:
			return 0

	def parseCountryName(self, countryName):
		return countryName

	def parseCurrencyName(self, currencyName):
		return currencyName

	def parseCurrencyAbbr(self, currencyAbbr):
		return currencyAbbr

