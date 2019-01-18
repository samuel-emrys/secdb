#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import logging
import re
import currency
import exchange
import symbol
import vendor
import price
import database
import configparser

from datetime import datetime
from vendor import Vendor


def build_database(vendor):
	con = database.connect()

	currency = []
	exchange = []
	symbols = []
	prices = []

	for vendor in vendors:
	# FIXME: This doesn't address the issue of merging data for insertion. 
	# Perhaps the scope of these functions should just be to obtain data before 
	# merging and populating the database
		# currency.append(vendor.build_currency())
		# exchange.append(vendor.build_exchanges())
		symbols.append(vendor.build_symbols())
		# prices.append(vendor.build_price())


	#Need to merge these elements


	# currency.build(con)
	# vendor.build(con)
	# exchange.build(con)
	# symbol.build(con)
	# price.build(con)

	# con.commit()
	# cur.close()
	# con.close()

def update_database():
	exit()

def help():
	print("Usage:")
	print("secdb --build");
	print('secdb --update');

def import_vendors():
	vendors = []
	config_filename = 'vendors.conf'
	
	# Load Configuration File
	config = configparser.RawConfigParser()
	config.read(config_filename)

	# Read Configuration Contents
	for vendor in config.sections():

		# print(config[vendor])

		# print(Vendor.parse_vendor(config.get(vendor, 'name')))

		vendor = Vendor.factory(vendor, config)

		# print(vendor)

		# name = parseVendor(config.get(vendor, 'name'))
		# website_url = parseVendor(config.get(vendor, 'website_url'))
		# support_email = parseVendor(config.get(vendor, 'support_email'))
		# api_url = parseVendor(config.get(vendor, 'api_url'))
		# api_key = parseVendor(config.get(vendor, 'api_key'))

		# now = datetime.utcnow()
		# created_date = now
		# last_updated_date = now
		if vendor is not None:
			vendors.append( vendor )

	return vendors

if __name__ == "__main__":
	arg = ""
	if (len(sys.argv) > 1):
		arg = sys.argv[1]
		now = datetime.utcnow()

	logging.basicConfig(filename='log/secdb.log',level=logging.DEBUG)

	vendors = import_vendors()

	now = datetime.utcnow()
	if (arg == "--build"):
		logging.info(str(now) + " Build option selected. Building database.")

		build_database(vendors)

	elif (arg == "--update"):
		logging.info(str(now) + " Update option selected. Updating database.")

		for vendor in vendors:
			vendor.update_currency()
			vendor.update_exchange()
			vendor.update_symbol()
			vendor.update_price()

		# update_database()

	elif (arg == "--help" or arg == "--h"):
		help()
	else:
		print('Invalid argument.')
		help()
		exit()
