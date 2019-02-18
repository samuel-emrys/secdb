# import psycopg2
# import logging
# from math import ceil
# from datetime import datetime


# from secdb.currency import Currency
# from secdb.symbol import Symbol
# from secdb.exchange import Exchange
# from secdb.price import Price
# from secdb.vendors.vendor import Vendor
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


def connect():
    db_host = "localhost"
    db_user = "postgres"
    db_pass = ""
    db_name = "securities_master"

    db_string = "postgresql://"+db_user+":"+db_pass+"@"+db_host+"/"+db_name
    db = create_engine(db_string)

    Session = sessionmaker(db)
    session = Session()
    Base.metadata.create_all(db)

    return session


# def connect():
#     db_host = "localhost"
#     db_user = "postgres"
#     db_pass = ""
#     db_name = "securities_master"

#     now = datetime.utcnow()

#     logging.info(
#         str(now)
#         + " Connecting to database "
#         + db_name
#         + " using credentials "
#         + db_user
#         + "@"
#         + db_host
#         + ":"
#         + db_pass
#     )

#     try:
#         con = psycopg2.connect(
#             "dbname="
#             + db_name
#             + " host="
#             + db_host
#             + " user="
#             + db_user
#             + " password="
#             + db_pass
#         )
#         logging.info(str(now) + " Connected!")
#         return con
#     except:
#         logging.exception(
#             str(now) + " Unable to connect to Database. Exiting."
#         )
#         exit()


# def insertmany(con, data, query):

#     cursor = con.cursor()
#     for i in range(0, int(ceil(len(data) / 100.0))):
#         try:
#             cursor.executemany(query, data[i * 100 : (i + 1) * 100 - 1])
#         except psycopg2.IntegrityError as e:
#             now = datetime.utcnow()
#             logging.error(str(now) + " " + str(e))

#     now = datetime.utcnow()
#     logging.info(
#         str(now) + " Inserted " + str(len(data)) + " entries into database."
#     )
