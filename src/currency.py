import requests
import database
import xml.etree.ElementTree as ET

def build(con):
	# Scrape ISO 4217 Currency information
	currencyURL = 'https://www.currency-iso.org/dam/downloads/lists/list_one.xml'
	response = requests.get(currencyURL)
	root = ET.fromstring(response.content)
	
	currencies = []
	countries = []
	currency_dict = dict()

	for country in root.find('CcyTbl').findall('CcyNtry'):

		countryName = parseCountryName(country.find('CtryNm').text)
		currencyName = parseCurrencyName(country.find('CcyNm').text)

		try:

			currencyAbbr = parseCurrencyAbbr(country.find('Ccy').text)
			currencyNum = country.find('CcyNbr').text
			currencyMinorUnit = parseMinorUnit(country.find('CcyMnrUnts').text)

			currency_dict[currencyAbbr] = currency_dict.get(currencyAbbr, 0) + 1
			countries.append( (countryName, currencyAbbr) )

		except AttributeError:
			currencyAbbr = None
			currencyNum = None
			currencyMinorUnit = None

		if (currencyAbbr is not None and currency_dict[currencyAbbr] == 1):
			currencies.append( (currencyAbbr, currencyNum, currencyName, currencyMinorUnit) )


	# for element in currencies:
	# 	print("%s | %s | %s | %s" % (element[0], element[1], element[2], element[3]))

	# for country in countries:
	# 	print("%s | %s" % (country[0], country[1]))

	columns = "code, num, currency, minor_unit"
	insert_str = ("%s, " * 4)[:-2]
	query = "INSERT INTO CURRENCY (%s) VALUES (%s);" % (columns, insert_str)
	database.insertmany(con, currencies, query)
	con.commit()

def parseMinorUnit(currencyMinorUnit):
	try:
		int(currencyMinorUnit)
		return currencyMinorUnit
	except ValueError:
		return 0

def parseCountryName(countryName):
	# countryName = countryName.encode("UTF-8")
	return countryName

def parseCurrencyName(currencyName):
	# currencyName = currencyName.encode("UTF-8")
	return currencyName

def parseCurrencyAbbr(currencyAbbr):
	# currencyAbbr = currencyAbbr.encode("UTF-8")
	return currencyAbbr


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


	# cursor.close()
