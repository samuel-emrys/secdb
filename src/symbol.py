import requests
import csv
import re
import io
import logging
import configparser
import helpers
import database
import requests, zipfile, io
import sys
from clint.textui import progress


from datetime import datetime
from lxml import html


def build(con):
	'''
		@TODO:
				Pull Historical ASX Symbols
					- Try to find whether these have been delisted or not, and create links with symbols that changed names
	'''
	sys.stderr.write("Building Symbols...")
	symbols = getASXHistoricalSymbols()
	symbols = getOtherASXETP(con, symbols)
	symbols = getASXCompanies(symbols)
	symbols = getWorldSymbols(con, symbols)

	# print(symbols)
	columns = "exchange_code, ticker, instrument, name, sector, currency, mer, benchmark, listing_date, created_date, last_updated_date"
	insert_str = ("%s, " * 11)[:-2]
	query = "INSERT INTO SYMBOL (%s) VALUES (%s);" % (columns, insert_str)
	database.insertmany(con, symbols, query)
	con.commit()

def getWorldSymbols(con, content):

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
	csvfile = io.StringIO(response.text, newline='')
	stocklist = csv.reader(csvfile)

	# Get list of abbreviations in exchange list
	cursor = con.cursor()
	query = "SELECT abbrev FROM EXCHANGE;"
	cursor.execute(query)
	cursorOutput = cursor.fetchall()
	exchangeList = [x[0] for x in cursorOutput]
	existingSymbols = [(x[1], x[0]) for x in content]


	# Parse symbols in the stocklist, and add them to list for addition to database
	for line in stocklist:

		exchange = helpers.removeWhitespace(line[4])
		name = helpers.removeWhitespace(line[1])
		currency = helpers.removeWhitespace(line[2])
		currency = parseCurrency(con, currency)
		symbolList = line[0].split('.')

		symbol = helpers.removeWhitespace(''.join(symbolList[:-1])) if len(symbolList) > 1 else helpers.removeWhitespace(symbolList[0])

		# print("%s | %s | %s | %s" % (symbol, name, currency, exchange))
		now = datetime.utcnow()
		createdDate = now
		lastUpdatedDate = now

		# print(symbol in exchangeList)
		if (exchange in exchangeList and currency != None):

			symbolPair = (symbol, exchange)
			if (symbolPair not in existingSymbols):
				content.append( (exchange, symbol, None, name, None, currency, None, None, None, now, now) )
				existingSymbols.append(symbolPair)

	return content

def getASXCompanies(symbols):

	## Scrape https://www.marketindex.com.au/asx-listed-companies to confirm list complete

	asxCompanyURL = 'https://www.asx.com.au/asx/research/ASXListedCompanies.csv'
	response = requests.get(asxCompanyURL)
	csvfile = io.StringIO(response.text, newline='')
	asxCompanies = csv.reader(csvfile)

	instrument = 'Shares'
	currency = 'AUD'
	exchange = 'ASX'
	MER = None
	benchmark = None
	existingSymbols = [(x[1], x[0]) for x in symbols]

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

			symbolPair = (ticker, exchange)
			if (symbolPair not in existingSymbols):
				symbols.append( (exchange, ticker, instrument, name, sector, currency, MER, benchmark, None, createdDate, lastUpdatedDate) );
				existingSymbols.append(symbolPair)

	return symbols

def getOtherASXETP(con, symbols):

	#Scrape https://www.asx.com.au/products/etf/managed-funds-etp-product-list.htm for other products
	asxETPURL = 'https://www.asx.com.au/products/etf/managed-funds-etp-product-list.htm'
	page = requests.get(asxETPURL)

	tree = html.fromstring(page.content)
	tr_elements = tree.xpath('//tr')
	# symbols = []

	# Initialise table entry values
	table_format = ""
	sector = None
	currency = 'AUD'
	exchange = 'ASX'
	existingSymbols = [(x[1], x[0]) for x in symbols]

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
				currency 		= parseCurrency(con, currency)
				mer 			= parseMER(mer)
				benchmark 		= parseBenchmark(benchmark)
				listingDate 	= parseListingDate(listingDate, '%b-%y')

				#print("%s | %s | %s | %s | %s | %s | %s | %s" % (name, ticker, instrument, sector, benchmark, MER, opFee, listingDate))
				now 			= datetime.utcnow()
				lastUpdatedDate = now
				createdDate 	= now


				symbolPair = (ticker, exchange)
				if (symbolPair not in existingSymbols):
					symbols.append( (exchange, ticker, instrument, name, sector, currency, mer, benchmark, listingDate, createdDate, lastUpdatedDate) );
					existingSymbols.append(symbolPair)

	return symbols

def getASXHistoricalSymbols():

	baseURL = 'https://www.asxhistoricaldata.com/data/'
	fileList = ['1997-2006.zip',
				'2007-2012.zip',
				'2013-2016.zip',
				'2017july-december.zip',
				'2017jan-june.zip',
				'2018july-sept.zip',
				'2018jan-june.zip']
	symbols = []
	exchange = 'ASX'
	currency = 'AUD'
	symbolCount = {}

	for f in fileList:
		url = baseURL + f
		sys.stderr.write("\n")
		print("Downloading %s from asxhistoricaldata.com" % f)

		headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:64.0) Gecko/20100101 Firefox/64.0'}
		
		# Download zip content
		r = requests.get(url, stream=True, headers=headers)
		total_length = int(r.headers.get('content-length'))
		content = []

		# Show progress bar
		for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1): 
			if chunk:
				# Append chunk to content list
				content.append(chunk)

		#Rejoin the zip file so it can be parsed
		download = b"".join(content)

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
				symbolCount[ticker] = symbolCount.get(ticker, 0) + 1
				# Make sure symbol is unique before adding to list
				# if ticker not in symbols:
				if symbolCount[ticker] == 1:
					now 			= datetime.utcnow()
					lastUpdatedDate = now
					createdDate 	= now

					symbols.append( (exchange, ticker, None, None, None, currency, None, None, None, createdDate, lastUpdatedDate) )

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

def parseCurrency(con, currency):
	cursor = con.cursor()
	query = "SELECT code FROM CURRENCY;"
	cursor.execute(query)
	cursorOutput = cursor.fetchall()
	currencyList = [x[0] for x in cursorOutput]

	if (currency not in currencyList):
		currency = None

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

	try:
		listingDate = datetime.strptime(listingDateString, dateFormat)

	except ValueError:
		listingDate = None

	return listingDate