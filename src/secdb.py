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
		currency.append(vendor.build_currency())
		exchange.append(vendor.build_exchanges())
		symbols.append(vendor.build_symbols())
		# prices.append(vendor.build_price())

def update_database():
	for vendor in vendors:	vendor.update_currency()
		vendor.update_exchange()
		vendor.update_symbol()
		vendor.update_price()
	
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
		vendor = Vendor.factory(vendor, config)
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

		# update_database()

	elif (arg == "--help" or arg == "--h"):
		help()
	else:
		print('Invalid argument.')
		help()
		exit()
