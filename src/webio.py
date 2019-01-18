import configparser
import requests
import re
import sys

from lxml import html
from clint.textui import progress



class WebIO:

	def login(url):

		session = requests.Session() # create a requests Session
		r = session.get(url)

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
		r2 = session.post(url, data=data_credentials)

		return session


	def download(url, file='', session = requests.Session()):

		# Find the base domain of the url to print
		urlStr = ''
		urlBase = re.search(r"^(?:https?:\/\/)?(?:[^@\/\n]+@)?(?:www\.)?([^:\/?\n]+)", url)
		if urlBase:
			urlStr = urlBase.group(1)

		content = []

		sys.stderr.write("\n")
		sys.stderr.write("Downloading %s from %s\n" % (file, urlStr))

		headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:64.0) Gecko/20100101 Firefox/64.0'}
		
		download_url = url + file

		# Download content
		r = session.get(download_url, stream=True, headers=headers)
		total_length = r.headers.get('content-length')

		if total_length is None:
			content.append(r.content)
			sys.stderr.write("[################################] 1/1 - 00:00:00")
		else:
			# Show progress bar
			total_length = int(total_length)
			for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1): 
				if chunk:
					# Append chunk to content list
					content.append(chunk)

		#Rejoin the file so it can be parsed
		download = b"".join(content)

		return download

