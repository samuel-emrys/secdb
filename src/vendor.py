
class Vendor:
	# Abstract vendor class, individual vendors inherit from this
	factory = staticmethod(factory)

	# Constructor
	def __init__(name, website_url, support_email, api_url, api_key):
		self.name = name
		self.website_url = website_url
		self.support_email = support_email
		self.api_url = api_url
		self.api_key = api_key

	# String overload
	def __str__(self):
		return self.name + "," + self.website_url + "," + self.support_email + "," +
			self.api_url + "," + self.api_key

	# Factory to generate appropriate subclass
	def factory(name, config):
		name = parseVendor(config.get(name, 'name'))
		website_url = parseVendor(config.get(name, 'website_url'))
		support_email = parseVendor(config.get(name, 'support_email'))
		api_url = parseVendor(config.get(name, 'api_url'))
		api_key = parseVendor(config.get(name, 'api_key'))

		if name == 'asx': 
			return VendorASX(name, website_url, support_email, api_url, api_key)
		elif name == 'alphavantage': 
			return VendorAlphaVantage()
		elif name == 'quandl': 
			return VendorQandl(name, website_url, support_email, api_url, api_key)
		elif name == 'worldtradingdata': 
			return VendorWorldTradingData(name, website_url, support_email, api_url, api_key)
		elif name == 'barchart': 
			return VendorBarchart()
		elif name == 'stooq': 
			return VendorStooq()
		elif name == 'iex': 
			return VendorIEX()
		elif name == 'asxhistoricaldata': 
			return VendorASXHistorical(name, website_url, support_email, api_url, api_key)
		elif name == 'marketindex': 
			return VendorMarketIndex(name, website_url, support_email, api_url, api_key)
		else:
			logging.INFO("Vendor '"+name+"' not currently supported. Skipping")


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
	def build_exchange(self):
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
	def __init__(name, website_url, support_email, api_url, api_key):
		super().__init__(name, website_url, support_email, api_url, api_key)
		self.company_url = 'https://www.asx.com.au/asx/research/ASXListedCompanies.csv'
		self.etp_url = 'https://www.asx.com.au/products/etf/managed-funds-etp-product-list.htm'

	def __str__(self):
		super().__str__(self)


	def build_symbols(self, symbols):
		## Scrape https://www.marketindex.com.au/asx-listed-companies to confirm list complete
		self.symbols = symbols

		build_companies(self)
		build_exchange_products(self)

		return self.symbols


	def build_companies(self, symbols):

		response = requests.get(self.company_url)
		csvfile = io.StringIO(response.text, newline='')
		companies = csv.reader(csvfile)

		instrument = 'Shares'
		currency = 'AUD'
		exchange = 'ASX'
		MER = None
		benchmark = None
		existing_symbols = [(x[1], x[0]) for x in symbols]

		count = 0
		for symbol in companies:
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
				created_date = now
				last_updated_date = now	

				symbol_pair = (ticker, exchange)
				if (symbol_pair not in existing_symbols):
					symbols.append( (exchange, ticker, instrument, name, sector, currency, MER, benchmark, None, created_date, last_updated_date) );
					existing_symbols.append(symbol_pair)

		return symbols

	def build_exchange_products(self, symbols):

		page = requests.get(self.etp_url)

		tree = html.fromstring(page.content)
		tr_elements = tree.xpath('//tr')

		# Initialise table entry values
		table_format = ""
		sector = None
		currency = 'AUD'
		exchange = 'ASX'
		existing_symbols = [(x[1], x[0]) for x in symbols]

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

					ticker 			= parseTicker(ticker)
					instrument 		= parseInstrument(instrument)
					name 			= parseName(name)
					sector 			= parseSector(sector)
					currency 		= parseCurrency(con, currency)
					mer 			= parseMER(mer)
					benchmark 		= parseBenchmark(benchmark)
					listing_date 	= parseListingDate(listing_date, '%b-%y')

					#print("%s | %s | %s | %s | %s | %s | %s | %s" % (name, ticker, instrument, sector, benchmark, MER, opFee, listingDate))
					now 			= datetime.utcnow()
					last_updated_date = now
					created_date 	= now


					symbol_pair = (ticker, exchange)
					if (symbol_pair not in existing_symbols):
						symbols.append( (exchange, ticker, instrument, name, sector, currency, mer, benchmark, listing_date, created_date, last_updated_date) );
						existing_symbols.append(symbol_pair)

		return symbols

class VendorWorldTradingData(Vendor):
	def __init__(name, website_url, support_email, api_url, api_key):
		super().__init__(name, website_url, support_email, api_url, api_key)
		self.stock_url = "https://www.worldtradingdata.com/download/list"
		self.login_url = "https://www.worldtradingdata.com/login"

	def __str__(self):
		super().__str__(self)

	def build_symbols(self):


		session = requests.Session() # create a requests Session
		r = session.get(self.login_url)

		### Get token
		tree = html.fromstring(r.content)
		token_value = tree.xpath('//input[@name="_token"]/@value')
		token = str(token_value[0])
		# Form credentials
		cred_filename = 'credentials.conf'
		
		# Load Configuration File
		credentials = configparser.RawConfigParser()
		credentials.read(cred_filename)

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
		cursor_out = cursor.fetchall()
		exchange_list = [x[0] for x in cursor_out]
		existing_symbols = [(x[1], x[0]) for x in content]


		# Parse symbols in the stocklist, and add them to list for addition to database
		for line in stocklist:

			exchange = helpers.removeWhitespace(line[4])
			name = helpers.removeWhitespace(line[1])
			currency = helpers.removeWhitespace(line[2])
			currency = parseCurrency(con, currency)
			symbol_list = line[0].split('.')

			symbol = helpers.removeWhitespace(''.join(symbol_list[:-1])) if len(symbol_list) > 1 else helpers.removeWhitespace(symbol_list[0])

			# print("%s | %s | %s | %s" % (symbol, name, currency, exchange))
			now = datetime.utcnow()
			created_date = now
			last_updated_date = now

			# print(symbol in exchangeList)
			if (exchange in exchange_list and currency != None):

				symbol_pair = (symbol, exchange)
				if (symbol_pair not in existing_symbols):
					content.append( (exchange, symbol, None, name, None, currency, None, None, None, created_date, last_updated_date) )
					existing_symbols.append(symbol_pair)

		return content


	def build_exchanges(self):

		session = requests.Session() # create a requests Session
		r = session.get(self.login_url)

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
		r2 = session.post(self.login_url, data=data_credentials)

		response = session.get(self.stock_url, timeout=(15,15))

		# response = requests.get(stockListURL)
		csvfile = io.StringIO(response.text, newline='')
		stocklist = csv.reader(csvfile)

		# Create map of suffixes
		# content = {}
		content = []
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

			if (exchange != 'N/A' and not re.match(r"(.*?)INDEX(.*)", exchange) and ' ' not in exchange):
				exchangeCount[exchange] = exchangeCount.get(exchange, 0) + 1
				if (exchangeCount[exchange] == 1):
					content.append( (exchange, suffix, exchangeDesc) )


		print(str(len(content)) + " items downloaded")

		content = addTZData(content)

		return content


	def addTZData(exchanges):
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
		content = []

		for row in tr_elements:
			# suffix = None
			first_element = row[0].text_content().strip().translate( { ord(c):None for c in '\n\t\r' } )

			if (len(row) == DATA_ROW_LENGTH and first_element != "Name"):
				name = parseName(row[NAME_ELEMENT].text_content())
				abbr = parseAbbr(row[ID_ELEMENT].text_content())
				country = parseCountry(row[COUNTRY_ELEMENT].text_content())
				city = parseCity(row[CITY_ELEMENT].text_content())
				zone = parseTimezone(row[ZONE_ELEMENT].text_content())
				delta = parseTZOffset(row[DELTA_ELEMENT].text_content())
				dst = parseDST(row[DST_ELEMENT].text_content())
				open_local = parseTime(row[OPEN_LOCAL_ELEMENT].text_content())
				close_local = parseTime(row[CLOSE_LOCAL_ELEMENT].text_content())
				open_utc = parseTime(row[OPEN_UTC_ELEMENT].text_content())
				close_utc = parseTime(row[CLOSE_UTC_ELEMENT].text_content())

				# suffixList = suffixes.get(abbr, 'N/A')

				# if (suffixList != 'N/A'):
				# 	suffix = suffixList[1]
				# else:
				# 	for key, values in suffixes.items():
				# 		# print(suffixList)
				# 		# print("%s, %s" % (values[0].upper(), name.upper()))

				# 		if (values[0].upper() == name.upper()):
				# 			suffix = values[1]
				# 			break
				# 			# TODO: Insert more advanced matching here

				now = datetime.utcnow()
				created_date = now
				last_updated_date = now

				wiki_exchanges[abbr] = (name, city, country, zone, delta, open_utc, close_utc, created_date, last_updated_date)
				# exchanges.append( (abbr, suffix, name, city, country, zone, delta, open_utc, close_utc, created_date, last_updated_date) )
				# print("%s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s" % (abbr, suffix, name, city, country, zone, delta, open_utc, close_utc, created_date, last_updated_date))

		for exchange in exchanges:
			abbr = exchange[0]
			suffix = exchange[1]
			exchangeDesc = exchange[2]

			exchangeData = wiki_exchanges.get(abbr, None)

			if (exchangeData != None):
				name = exchangeData[0]
				city = exchangeData[1]
				country = exchangeData[2]
				zone = exchangeData[3]
				delta = exchangeData[4]
				open_utc = exchangeData[5]
				close_utcs = exchangeData[6]
				created_date = exchangeData[7]
				last_updated_date = exchangeData[8]

				content.append( (abbr, suffix, exchangeDesc, city, country, zone, delta, open_utc, close_utc, created_date, last_updated_date) )
			else:
				now = datetime.utcnow()
				created_date = now
				last_updated_date = now
				content.append( (abbr, suffix, exchangeDesc, None, None, None, None, None, None, created_date, last_updated_date) )

		return content

class VendorASXHistorical(Vendor):
	def __init__(name, website_url, support_email, api_url, api_key):
		super().__init__(name, website_url, support_email, api_url, api_key)
		self.fileList = ['1997-2006.zip',
					'2007-2012.zip',
					'2013-2016.zip',
					'2017july-december.zip',
					'2017jan-june.zip',
					'2018july-sept.zip',
					'2018jan-june.zip']
		self.exchange = 'ASX'
		self.currency = 'AUD'

	def __str__(self):
		super().__str__(self)

	def build_symbols(self):
		
		symbol_count = {}

		for f in self.fileList:
			url = self.api_url + f
			sys.stderr.write("\n")
			sys.stderr.write("Downloading %s from asxhistoricaldata.com" % f)

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
					symbol_count[ticker] = symbol_count.get(ticker, 0) + 1
					# Make sure symbol is unique before adding to list
					# if ticker not in symbols:
					if symbol_count[ticker] == 1:
						now 			= datetime.utcnow()
						last_updated_date = now
						created_date 	= now

						symbols.append( (self.exchange, ticker, None, None, None, self.currency, None, None, None, created_date, last_updated_date) )

		return symbols

class VendorMarketIndex(Vendor):
	def __init__(name, website_url, support_email, api_url, api_key):
		super().__init__(name, website_url, support_email, api_url, api_key)

	def __str__(self):
		super().__str__(self)

class VendorQandl(Vendor):
	def __init__(name, website_url, support_email, api_url, api_key):
		super().__init__(name, website_url, support_email, api_url, api_key)

	def __str__(self):
		super().__str__(self)

class VendorQandl(Vendor):
	def __init__(name, website_url, support_email, api_url, api_key):
		super().__init__(name, website_url, support_email, api_url, api_key)

	def __str__(self):
		super().__str__(self)

class VendorAlphaVantage(Vendor):
	def __init__(name, website_url, support_email, api_url, api_key):
		super().__init__(name, website_url, support_email, api_url, api_key)

	def __str__(self):
		super().__str__(self)

class VendorBarchart(Vendor):
	def __init__(name, website_url, support_email, api_url, api_key):
		super().__init__(name, website_url, support_email, api_url, api_key)

	def __str__(self):
		super().__str__(self)

class VendorStooq(Vendor):
	def __init__(name, website_url, support_email, api_url, api_key):
		super().__init__(name, website_url, support_email, api_url, api_key)

	def __str__(self):
		super().__str__(self)

class VendorIEX(Vendor):
	def __init__(name, website_url, support_email, api_url, api_key):
		super().__init__(name, website_url, support_email, api_url, api_key)

	def __str__(self):
		super().__str__(self)
