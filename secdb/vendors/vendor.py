from utils.webio import WebIO
from abc import abstractmethod
from datetime import datetime
from datetime import timedelta
from lxml import html
from urllib.parse import urlparse

import configparser
import utils.helpers as helpers
import logging
import string
import requests
import csv
import io
import re
import zipfile
import sys
import xml.etree.ElementTree as ET
import json
import time

from exchange import Exchange
from currency import Currency
from symbol import Symbol
from price import Price


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
		ticker = helpers.removeWhitespace(ticker)

		# Could also check that it contains only uppercase characters, length 3-5 (what's the maximum ticker length?)
		return ticker

	def parseInstrument(self, instrument):
		# Remove extraneous white space from left and right of string, and remove tabs/new line characters from middle of string
		instrument = helpers.removeWhitespace(instrument)

		return instrument

	def parseName(self, name):
		# Remove extraneous white space from left and right of string, and remove tabs/new line characters from middle of string
		name = helpers.removeWhitespace(name)

		return name

	def parseSector(self, sector):
		if (sector != None):
			# Remove extraneous white space from left and right of string, and remove tabs/new line characters from middle of string
			sector = helpers.removeWhitespace(sector)

			if (sector == "#" or sector == "Not Applic"):
				sector = None

		return sector

	def parseCurrency(self, currency):

		if (currency not in self.currencies):
			currency = None

		return currency

	def parseMER(self, mer):
		if (mer != None):
			# Remove extraneous white space from left and right of string, and remove tabs/new line characters from middle of string
			mer = helpers.removeWhitespace(mer)

			if (mer == "-"):
				mer = None
			# else if string doesn't match a decimal
			elif not (re.match(r"^[0-9]{1,2}(.[0-9]+?)?$", mer)):
				# now = datetime.utcnow()
				# logging.debug(str(now) + " Invalid MER ' " + mer + "' identified. Sanitized with 'None'.")
				mer = None

		return mer

	def parseBenchmark(self, benchmark):
		if (benchmark != None):
			# Remove extraneous white space from left and right of string, and remove tabs/new line characters from middle of string
			benchmark = helpers.removeWhitespace(benchmark)

			if (benchmark == "-"):
				benchmark = None

		return benchmark

	def parse_date(self, date, date_format):
		
		# Remove extraneous white space from left and right of string, and remove tabs/new line characters from middle of string
		date_str = helpers.removeWhitespace(date)

		try:
			date = datetime.strptime(date, date_format)

		except ValueError:
			date = None

		return date


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
		return abbr

	def parseCountry(self, country):
		country = helpers.removeWhitespace(country)
		country = helpers.removeWikipediaReferences(country)
		return country

	def parseCity(self, city):
		city = helpers.removeWhitespace(city)
		city = helpers.removeWikipediaReferences(city)
		return city

	def parseTimezone(self, timezone):
		timezone = helpers.removeWhitespace(timezone)
		timezone = helpers.removeWikipediaReferences(timezone)
		return timezone

	def parseTZOffset(self, delta):
		delta = helpers.removeWhitespace(delta)
		delta = helpers.removeWikipediaReferences(delta)
		delta = delta.replace("−", "-"); 
		delta = timedelta(hours=float(delta))

		return delta

	def parseDST(self, dst):
		dst = helpers.removeWhitespace(dst)
		dst = helpers.removeWikipediaReferences(dst)
		return dst

	def parseTime(self, time):
		time = helpers.removeWhitespace(time)
		time = helpers.removeWikipediaReferences(time)
		time = datetime.strptime(time,"%H:%M").time()

		return time


	# Price Helper Methods

	def parse_price(self, price):
		price = helpers.removeWhitespace(price)
		price = price.replace('$','')

		return price

	# Factory to generate appropriate subclass
	# def factory(title, config):
	# 	name = Vendor.parse_vendor(config.get(title, 'name'))
	# 	website_url = Vendor.parse_vendor(config.get(title, 'website_url'))
	# 	support_email = Vendor.parse_vendor(config.get(title, 'support_email'))
	# 	api_url = Vendor.parse_vendor(config.get(title, 'api_url'))
	# 	api_key = Vendor.parse_vendor(config.get(title, 'api_key'))
	# 	now = datetime.utcnow()

	# 	if title == 'asx': 
	# 		return VendorASX(name, website_url, support_email, api_url, api_key)
	# 	elif title == 'alphavantage': 
	# 		logging.info(str(now) + ": Vendor '"+name+"' not currently supported. Skipping")
	# 	elif title == 'quandl': 
	# 		logging.info(str(now) + ": Vendor '"+name+"' not currently supported. Skipping")
	# 	elif title == 'worldtradingdata': 
	# 		return VendorWorldTradingData(name, website_url, support_email, api_url, api_key)
	# 	elif title == 'barchart': 
	# 		logging.info(str(now) + ": Vendor '"+name+"' not currently supported. Skipping")
	# 	elif title == 'stooq': 
	# 		logging.info(str(now) + ": Vendor '"+name+"' not currently supported. Skipping")
	# 	elif title == 'iex': 
	# 		logging.info(str(now) + ": Vendor '"+name+"' not currently supported. Skipping")
	# 	elif title == 'asxhistoricaldata': 
	# 		return VendorASXHistorical(name, website_url, support_email, api_url, api_key)
	# 	elif title == 'marketindex': 
	# 		return VendorMarketIndex(name, website_url, support_email, api_url, api_key)
	# 	elif title == 'currencyiso':
	# 		return VendorCurrencyISO(name, website_url, support_email, api_url, api_key)
	# 	else:
	# 		logging.info(str(now) + ": Vendor '"+name+"' not currently supported. Skipping")


	# factory = staticmethod(factory)


	# Build methods
	@abstractmethod
	def build_symbols(self, currencies, exchanges):
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







