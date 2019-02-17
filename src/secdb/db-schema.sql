CREATE TABLE CURRENCY(
	code 					VARCHAR(32)  	NOT	NULL 							,
	num						INTEGER 			NULL							,
	currency 				VARCHAR(255) 		NULL 							,
	minor_unit 				INTEGER 			NULL							,
	PRIMARY KEY 			(code) 												
);

CREATE TABLE EXCHANGE(
	abbrev 					VARCHAR(32)		NOT NULL UNIQUE						,
	suffix 					VARCHAR(32) 		NULL							,
	name 					VARCHAR(255)	NOT NULL							,
	city 					VARCHAR(255)		NULL							,
	country 				VARCHAR(255)		NULL							,
	timezone 				VARCHAR(64) 		NULL 							,
	timezone_offset			TIME 				NULL							,
	open_utc				TIME 				NULL 							,
	close_utc 				TIME 				NULL 							,
	created_date			TIMESTAMP 		NOT NULL							,
	last_updated_date 		TIMESTAMP 		NOT NULL							,
	PRIMARY KEY 			(abbrev)											
);

CREATE TABLE DATA_VENDOR(
	id 						SERIAL 												,
	name 					VARCHAR(64)		NOT	NULL							,
	website_url 			VARCHAR(255)		NULL							,
	support_email 			VARCHAR(255)		NULL							,
	created_date			TIMESTAMP 		NOT NULL							,
	last_updated_date 		TIMESTAMP 		NOT NULL							,
	PRIMARY KEY				(id)
);

CREATE TABLE SYMBOL(
	id 						SERIAL 												,
	prev_id 				INTEGER 			NULL							,
	exchange_code 			VARCHAR(32) 	NOT	NULL							,
	ticker 					VARCHAR(32) 	NOT NULL							,
	instrument 				VARCHAR(64) 		NULL							,
	name 					VARCHAR(255) 		NULL							,
	sector 					VARCHAR(255)		NULL							,
	currency 				VARCHAR(32) 		NULL							,
	mer 					DECIMAL(13,10)		NULL							,
	benchmark				VARCHAR(255) 		NULL							,
	listing_date 			TIMESTAMP 			NULL							,
	created_date 			TIMESTAMP 		NOT NULL							,
	last_updated_date 		TIMESTAMP 		NOT NULL							,
	UNIQUE 					(ticker, exchange_code) 							,
	PRIMARY KEY 			(id)												,
	FOREIGN KEY 			(exchange_code)	REFERENCES 		EXCHANGE(abbrev)	,
	FOREIGN KEY 			(prev_id) 		REFERENCES 		SYMBOL(id)			,
	FOREIGN KEY 			(currency) 		REFERENCES 		CURRENCY(code)
);

CREATE TABLE DAILY_PRICE(
	id 						SERIAL 												,
	data_vendor_id 			INTEGER 		NOT NULL							,
	symbol_id 				INTEGER 		NOT NULL							,
	price_date 				TIMESTAMP 		NOT NULL							,
	open_price 				DECIMAL(19,4) 		NULL							,
	high_price 				DECIMAL(19,4) 		NULL							,
	low_price 				DECIMAL(19,4) 		NULL							,
	close_price 			DECIMAL(19,4) 		NULL							,
	adj_close_price 		DECIMAL(19,4) 		NULL							,
	volume 					BIGINT 				NULL							,
	created_date			TIMESTAMP 		NOT NULL							,
	last_updated_date 		TIMESTAMP 		NOT NULL							,
	PRIMARY KEY 			(id) 												,
	FOREIGN KEY 			(data_vendor_id) 	REFERENCES DATA_VENDOR(id) 		,
	FOREIGN KEY 			(symbol_id) 		REFERENCES SYMBOL(id) 			
);


