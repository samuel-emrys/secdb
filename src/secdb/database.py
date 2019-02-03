import psycopg2
import logging

from math import ceil
from datetime import datetime


def connect():
    db_host = "localhost"
    db_user = "secdb_admin"
    db_pass = "Default123!"
    db_name = "securities_master"

    now = datetime.utcnow()

    logging.info(
        str(now)
        + " Connecting to database "
        + db_name
        + " using credentials "
        + db_user
        + "@"
        + db_host
        + ":"
        + db_pass
    )

    try:
        con = psycopg2.connect(
            "dbname="
            + db_name
            + " host="
            + db_host
            + " user="
            + db_user
            + " password="
            + db_pass
        )
        logging.info(str(now) + " Connected!")
        return con
    except:
        logging.exception(
            str(now) + " Unable to connect to Database. Exiting."
        )
        exit()


def insertmany(con, data, query):

    cursor = con.cursor()
    for i in range(0, int(ceil(len(data) / 100.0))):
        try:
            cursor.executemany(query, data[i * 100 : (i + 1) * 100 - 1])
        except psycopg2.IntegrityError as e:
            now = datetime.utcnow()
            logging.error(str(now) + " " + str(e))

    now = datetime.utcnow()
    logging.info(
        str(now) + " Inserted " + str(len(data)) + " entries into database."
    )
