# secdb

secdb is a financial market data aggregation program. It aggregates data from a number of websites and freely available APIs to build and maintain a SQL database. This 
database can then be used as a source for financial market analysis with confidence.

secdb will maintain the following data:

* ISO 4217 Currency Information
* Stock Exchanges
	* Name
	* Abbreviation
	* Ticker Suffix
	* City/Country
	* Currency
	* Region Timezone (UTC)
	* Timezone Offset
	* Exchange Open and Close Time (UTC)

* Data Vendors
	* Name
	* URL
	* API Key

* Symbols
	* Ticker
	* Name
	* Sector
	* Currency
	* Instrument Type
	* Listed Stock Exchange
	* Benchmark (where applicable)
	* Listing date (where applicable)

* Daily Prices
	* Date
	* Open
	* High
	* Low
	* Close
	* Volume

## Dependencies

Python 3.5.2 or higher
psycopg2
requests
PostgreSQL

## Installation

TBD

## Configuration

TBD

## Usage

secdb --build

secdb --update
