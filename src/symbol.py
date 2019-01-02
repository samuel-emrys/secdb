import requests
import csv
import re
import io
import logging

from datetime import datetime
from lxml import html


def build():
	'''
		@TODO:
				Incorporate worldtradingdata tickers
				Revise database schema
				Source API's:
					- https://www.worldtradingdata.com/download/list (Stocks)
					- https://www.worldtradingdata.com/download/mutual/list (Mutual Funds)
	'''


	companySymbols = getCompanies()
	otherSymbols = getOtherETP()

	symbols = companySymbols + otherSymbols

	for symbol in symbols:
		print("%s | %s | %s | %s | %s | %s | %s | %s | %s" % (symbol[0], symbol[1], symbol[2], symbol[3], symbol[4], symbol[5], symbol[6], symbol[7], symbol[8]))


	# column_str = "ticker, instrument, name, sector, currency, listing_date, last_updated_date"
	# insert_str = ("%s, " * 7)[:-2]
	# final_str = "INSERT INTO SYMBOL (%s) VALUES (%s);" % (column_str, insert_str)

	# now = datetime.utcnow()
	# try:
	# 	con = connectToDatabase()
	# 	logging.info(str(now) + " Connected!")
	# except:
	# 	logging.exception(str(now) + " Unable to connect to Database. Exiting.")
	# 	exit()

	# cursor = con.cursor();
	# for i in range(0, int(ceil(len(symbols) / 100.0))):
	# 	cursor.executemany(final_str, symbols[i*100:(i+1)*100-1])


	# con.commit()
	# cur.close()
	# conn.close()

def getCompanies():
	asxCompanyURL = 'https://www.asx.com.au/asx/research/ASXListedCompanies.csv'
	response = requests.get(asxCompanyURL)
	csvfile = io.StringIO(response.text, newline='')
	asxCompanies = csv.reader(csvfile)


	symbols = []
	instrument = 'Shares'
	currency = 'AUD'
	MER = None
	benchmark = None


	count = 0;
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
			listingDate = now
			lastUpdatedDate = now
			symbols.append( (ticker, instrument, name, sector, currency, MER, benchmark, listingDate, lastUpdatedDate) );

	return symbols

def getOtherETP():

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
				symbols.append( (ticker, instrument, name, sector, currency, mer, benchmark, listingDate, lastUpdatedDate) );

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