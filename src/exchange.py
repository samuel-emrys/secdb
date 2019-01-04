import requests
# import re
import database
import helpers
import io
import csv
import configparser

from datetime import datetime
from datetime import timedelta
from datetime import time
from lxml import html

# def build(con):
# 	getSuffixes()

def build(con):
	'''
		@TODO
			Work out how to associate a currency with an exchange - currencies are currently unpopulated
	'''

	suffixes = getSuffixes()

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
	exchanges = []

	for row in tr_elements:
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

			now = datetime.utcnow()
			created_date = now
			last_updated_date = now

			exchanges.append( (abbr, name, city, country, zone, delta, open_utc, close_utc, created_date, last_updated_date) )
			# print("%s | %s | %s | %s | %s | %s | %s | %s | %s | %s" % (abbr, name, city, country, zone, delta, open_utc, close_utc, created_date, last_updated_date))
	
	columns = "abbrev, name, city, country, timezone, timezone_offset, open_time, close_time, created_date, last_updated_date"
	insert_str = ("%s, " * 10)[:-2]
	query = "INSERT INTO EXCHANGE (%s) VALUES (%s);" % (columns, insert_str)
	database.insertmany(con, exchanges, query)


def getSuffixes():
	# - https://www.worldtradingdata.com/download/list (Stocks)

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

	content = []
	for line in stocklist:
		content.append(line)

	print(str(len(content)) + " items downloaded")

def parseName(name):
	name = helpers.removeWhitespace(name)
	name = helpers.removeWikipediaReferences(name)

	return name

def parseAbbr(abbr):
	abbr = helpers.removeWhitespace(abbr)
	abbr = helpers.removeWikipediaReferences(abbr)

	# abbr = re.sub(r"\[.*\]","", abbr)
	return abbr

def parseCountry(country):
	country = helpers.removeWhitespace(country)
	country = helpers.removeWikipediaReferences(country)
	# country = re.sub(r"\[.*\]","", country)
	return country

def parseCity(city):
	city = helpers.removeWhitespace(city)
	city = helpers.removeWikipediaReferences(city)
	# city = re.sub(r"\[.*\]","", city)
	return city

def parseTimezone(timezone):
	timezone = helpers.removeWhitespace(timezone)
	timezone = helpers.removeWikipediaReferences(timezone)
	# timezone = re.sub(r"\[.*\]","", timezone)
	return timezone

def parseTZOffset(delta):
	delta = helpers.removeWhitespace(delta)
	delta = helpers.removeWikipediaReferences(delta)
	delta = delta.replace("−", "-"); 
	# delta = re.sub(r"\[.*\]","", delta)
	delta = timedelta(hours=float(delta))

	return delta

def parseDST(dst):
	dst = helpers.removeWhitespace(dst)
	dst = helpers.removeWikipediaReferences(dst)
	# dst = re.sub(r"\[.*\]","", dst)
	return dst

def parseTime(time):
	time = helpers.removeWhitespace(time)
	time = helpers.removeWikipediaReferences(time)
	# time = re.sub(r"\[.*\]","", time)
	time = datetime.strptime(time,"%H:%M").time()

	return time

