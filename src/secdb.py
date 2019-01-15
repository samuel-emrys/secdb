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

from datetime import datetime


def build_database():
	con = database.connect()

	# f_string = '-3'
	# print(f_string + ": " + str(type(f_string)))
	# f = float(f_string)
	# print(str(f) + ": " + str(type(f)))

	# out = re.match(r"(.*?)INDEX(.*)", "INDEXSTOXX")
	# out = re.match(r"(.*?)INDEX(.*)", "fdsgdh")
	# print(out)


	# currency.build(con)
	# vendor.build(con)
	# exchange.build(con)
	symbol.build(con)
	# price.build(con)

	# con.commit()
	# cur.close()
	con.close()

def update_database():
	exit()

def help():
	print("Usage:")
	print("secdb --build");
	print('secdb --update');


if __name__ == "__main__":
	arg = ""
	if (len(sys.argv) > 1):
		arg = sys.argv[1]
		now = datetime.utcnow()

	logging.basicConfig(filename='log/secdb.log',level=logging.DEBUG)

	now = datetime.utcnow()
	if (arg == "--build"):
		logging.info(str(now) + " Build option selected. Building database.")
		build_database()

	elif (arg == "--update"):
		logging.info(str(now) + " Update option selected. Updating database.")
		update_database()

	elif (arg == "--help" or arg == "--h"):
		help()
	else:
		print('Invalid argument.')
		help()
		exit()
