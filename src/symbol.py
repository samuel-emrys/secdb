import requests
import csv
import re
import io
import logging
import configparser
import helpers

from datetime import datetime
from lxml import html


def build(con):
	'''
		@TODO:
				Incorporate worldtradingdata tickers
				Source API's:
					- https://www.worldtradingdata.com/download/list (Stocks)
					- https://www.worldtradingdata.com/download/mutual/list (Mutual Funds)
	'''

	worldSymbols = getWorldSymbols(con)
	# companySymbols = getASXCompanies()
	# otherSymbols = getOtherASXETP()

	# cursor = con.cursor()
	# query = "SELECT abbrev, id FROM EXCHANGE;"
	# cursor.execute(query)

	# exchangeIDList = cursor.fetchall()

	# exchangeID = dict(exchangeIDList)

	# worldSymbols = []

	# for symbol in worldSymbolsUnparsed:
	# 	symid = exchangeID.get(symbol[0], None)
	# 	symbol = list(symbol)
	# 	symbol[0] = symid
	# 	symbol = tuple(symbol)
	# 	# print(symid)
	# 	worldSymbols.append(symbol)


	# worldSymbols = [i for i in worldSymbols if i[0] != None ]
	# print(worldSymbols)
	# symbols = companySymbols + otherSymbols

	print(len(worldSymbols))
	for symbol in worldSymbols:
		print(symbol)

	columns = "exchange, ticker, instrument, name, sector, currency, mer, benchmark, listing_date, created_date, last_updated_date"
	insert_str = ("%s, " * 11)[:-2]
	query = "INSERT INTO SYMBOL (%s) VALUES (%s);" % (columns, insert_str)
	# database.insertmany(con, symbols, query)

def getWorldSymbols(con):

	stockListURL = "https://www.worldtradingdata.com/download/list"
	login_url = "https://www.worldtradingdata.com/login"

	session = requests.Session() # create a requests Session
	r = session.get(login_url)

	### Get token
	tree = html.fromstring(r.content)
	tokenValue = tree.xpath('//input[@name="_token"]/@value')
	token = str(tokenValue[0])
	# Form credentials
	credentialsFilename = 'credentials.conf'
	
	# Load Configuration File
	credentials = configparser.RawConfigParser()
	credentials.read(credentialsFilename)

	for cred in credentials.sections():
		email = credentials.get(cred, 'user')
		password = credentials.get(cred, 'password')

	# Create credentials dictionary
	data_credentials = {'email': email, 'password': password, '_token': token}

	# Log in to requests session, send post
	r2 = session.post(login_url, data=data_credentials)

	response = session.get(stockListURL, timeout=(15,15))

	# response = requests.get(stockListURL)
	csvfile = io.StringIO(response.text, newline='')
	stocklist = csv.reader(csvfile)

	# Get list of abbreviations in exchange list
	cursor = con.cursor()
	query = "SELECT abbrev FROM EXCHANGE;"
	cursor.execute(query)
	exchangeList = cursor.fetchall()
	print(exchangeList)

	# Create list of symbols
	content = []
	# Create dataset of symbols
	for line in stocklist:

		exchange = helpers.removeWhitespace(line[4])
		name = helpers.removeWhitespace(line[1])
		currency = helpers.removeWhitespace(line[2])
		symbolList = line[0].split('.')

		symbol = helpers.removeWhitespace(''.join(symbolList[:-1])) if len(symbolList) > 1 else helpers.removeWhitespace(symbolList[0])

		# print("%s | %s | %s | %s" % (symbol, name, currency, exchange))
		now = datetime.utcnow()
		createdDate = now
		lastUpdatedDate = now

		print(symbol in exchangeList)
		if (symbol in exchangeList):
			content.append( (exchange, symbol, None, name, None, currency, None, None, None, now, now) )

	return content

def getASXCompanies():
	asxCompanyURL = 'https://www.asx.com.au/asx/research/ASXListedCompanies.csv'
	response = requests.get(asxCompanyURL)
	csvfile = io.StringIO(response.text, newline='')
	asxCompanies = csv.reader(csvfile)


	symbols = []
	instrument = 'Shares'
	currency = 'AUD'
	exchange = 'ASX'
	MER = None
	benchmark = None


	count = 0
	for symbol in asxCompanies:
		count+=1; #counts the number of lines before entries should be entered (truncates first 3 lines)

		if (len(symbol) > 0 and count > 3):
			ticker = None;
			name = symbol[0];
			sector = None;
			if (len(symbol) == 2):
				ticker = symbol[1];
			elif (len(symbol) == 3):
				ticker = symbol[1];
				sector = symbol[2];

			# Create a tuple in DB format and append to total list.
			# Need to add query to DB to check if ticker already exists. If it doesn't, add "now" as created date, otherwise leave no entry for this
			
			sector = parseSector(sector)

			now = datetime.utcnow()
			createdDate = now
			lastUpdatedDate = now
			symbols.append( (exchange, ticker, instrument, name, sector, currency, MER, benchmark, None, createdDate, lastUpdatedDate) );

	return symbols

def getOtherASXETP():

	#Scrape https://www.asx.com.au/products/etf/managed-funds-etp-product-list.htm for other products
	asxETPURL = 'https://www.asx.com.au/products/etf/managed-funds-etp-product-list.htm'
	page = requests.get(asxETPURL)

	tree = html.fromstring(page.content)
	tr_elements = tree.xpath('//tr')
	symbols = []

	# Initialise table entry values
	table_format = ""
	sector = None
	currency = 'AUD'
	exchange = 'ASX'

	for row in tr_elements:
		first_element = row[0].text_content().strip().translate( { ord(c):None for c in '\n\t\r' } )

		# Identify which table is being parsed and define table format
		if (first_element == "Exposure"):
			if (len(row) == 9):
				table_format = "LIC"
			elif (len(row) == 6):
				table_format = "AREITS"
			elif (len(row) == 10 and row[3].text_content().strip() == "iNAV Code"):
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
				listingDate 	= row[6].text_content()

			elif (table_format == "AREITS"):

				name 			= row[0].text_content()
				ticker 			= row[1].text_content()
				instrument 		= row[2].text_content()
				benchmark 		= None
				mer 			= None
				listingDate 	= row[3].text_content()

			elif (table_format == "ETP"):

				name 			= row[0].text_content()
				ticker 			= row[1].text_content()
				instrument 		= row[2].text_content()
				benchmark 		= row[4].text_content()
				mer 			= row[6].text_content()
				listingDate 	= row[7].text_content()

			elif (table_format == "ETP_SINGLE_ASSET"):

				name 			= row[0].text_content()
				ticker 			= row[1].text_content()
				instrument 		= row[2].text_content()
				benchmark 		= row[4].text_content()
				mer 			= row[6].text_content()
				listingDate 	= row[7].text_content()

			elif (table_format == "INFRASTRUCTURE"):
				name 			= row[0].text_content()
				ticker 			= row[1].text_content()
				instrument 		= row[2].text_content()
				sector 			= row[3].text_content()
				benchmark 		= None
				mer 			= None
				listingDate 	= row[4].text_content()

			elif (table_format == "ABS_RETURN_FUNDS"):

				name 			= row[0].text_content()
				ticker 			= row[1].text_content()
				instrument 		= row[2].text_content()
				sector 			= None
				benchmark 		= row[3].text_content()
				mer 			= row[4].text_content()
				listingDate 	= row[5].text_content()

			elif (table_format == "PDFs"):
				name 			= row[0].text_content()
				ticker 			= row[1].text_content()
				instrument 		= row[2].text_content()
				sector 			= None
				benchmark 		= None
				mer 			= None
				listingDate 	= row[3].text_content()


			if (len(row) > 1):

				ticker 			= parseTicker(ticker)
				instrument 		= parseInstrument(instrument)
				name 			= parseName(name)
				sector 			= parseSector(sector)
				currency 		= parseCurrency(currency)
				mer 			= parseMER(mer)
				benchmark 		= parseBenchmark(benchmark)
				listingDate 	= parseListingDate(listingDate, '%b-%y')

				#print("%s | %s | %s | %s | %s | %s | %s | %s" % (name, ticker, instrument, sector, benchmark, MER, opFee, listingDate))
				now 			= datetime.utcnow()
				lastUpdatedDate = now
				createdDate 	= now
				symbols.append( (exchange, ticker, instrument, name, sector, currency, mer, benchmark, listingDate, createdDate, lastUpdatedDate) );

	return symbols


def parseTicker(ticker):
	# Remove extraneous white space from left and right of string, and remove tabs/new line characters from middle of string
	ticker = ticker.strip().translate( { ord(c):None for c in '\n\t\r' } )

	# Could also check that it contains only uppercase characters, length 3-5 (what's the maximum ticker length?)
	return ticker

def parseInstrument(instrument):
	# Remove extraneous white space from left and right of string, and remove tabs/new line characters from middle of string
	instrument = instrument.strip().translate( { ord(c):None for c in '\n\t\r' } )

	return instrument

def parseName(name):
	# Remove extraneous white space from left and right of string, and remove tabs/new line characters from middle of string
	name = name.strip().translate( { ord(c):None for c in '\n\t\r' } )

	return name

def parseSector(sector):
	if (sector != None):
		# Remove extraneous white space from left and right of string, and remove tabs/new line characters from middle of string
		sector = sector.strip().translate( { ord(c):None for c in '\n\t\r' } )

		if (sector == "#" or sector == "Not Applic"):
			sector = None

	return sector

def parseCurrency(currency):
	#mostly just a placeholder for future exchange data inclusion
	return currency


def parseMER(mer):
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

def parseBenchmark(benchmark):
	if (benchmark != None):
		# Remove extraneous white space from left and right of string, and remove tabs/new line characters from middle of string
		benchmark = benchmark.strip().translate( { ord(c):None for c in '\n\t\r' } )

		if (benchmark == "-"):
			benchmark = None

	return benchmark

def parseListingDate(listingDate, dateFormat):
	
	# Remove extraneous white space from left and right of string, and remove tabs/new line characters from middle of string
	listingDateString = listingDate.strip().translate( { ord(c):None for c in '\n\t\r' } )
	#listingDate = datetime.strptime('Jun 1 2005  1:33PM', '%b %d %Y %I:%M%p')
	# listingDate = datetime.strptime('Jan-06', '%b-%y')
	#if (listingDateString is not ''):
	try:
		listingDate = datetime.strptime(listingDateString, dateFormat)

	except ValueError:
		listingDate = None

	return listingDate