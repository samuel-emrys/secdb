import database
import configparser
import io
import helpers
from datetime import datetime

def build(con):
	'''
	@input: Connection to the database
	@TODO: 
			Implement configuration file for vendors
			Add api url to database
				Do I need to specify type of api?
				Multiple API URLs?
			Add API key to database
	'''
	vendors = []
	configFilename = 'vendors.conf'
	
	# Load Configuration File
	config = configparser.RawConfigParser()
	config.read(configFilename)

	# Read Configuration Contents
	for vendor in config.sections():
		name = parseVendor(config.get(vendor, 'name'))
		website_url = parseVendor(config.get(vendor, 'website_url'))
		support_email = parseVendor(config.get(vendor, 'support_email'))
		api_url = parseVendor(config.get(vendor, 'api_url'))
		api_key = parseVendor(config.get(vendor, 'api_key'))

		now = datetime.utcnow()
		created_date = now
		last_updated_date = now

		vendors.append( (name, website_url, support_email, api_url, api_key, created_date, last_updated_date) )


	# for vendor in vendors:
	# 	print("%s | %s | %s | %s | %s | %s | %s" % (vendor[0], vendor[1], vendor[2], vendor[3], vendor[4], vendor[5], vendor[6]))

	columns = "name, website_url, support_email, api_url, api_key, created_date, last_updated_date"
	insert_str = ("%s, " * 7)[:-2]
	query = "INSERT INTO DATA_VENDOR (%s) VALUES (%s);" % (columns, insert_str)
	database.insertmany(con, vendors, query)

def parseVendor(element):
	element = helpers.removeWhitespace(element)

	if (element == 'NA' or element == ''):
		return None

	return element