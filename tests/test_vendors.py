from secdb.vendors.vendor import Vendor
from sqlalchemy import create_engine
from secdb.database import Base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from secdb.application import import_vendors


'''
    Initialisation variables
'''
db_host = "localhost"
db_user = "postgres"
db_pass = ""
db_name = "securities_master"

db_string = "postgresql://"+db_user+":"+db_pass+"@"+db_host+"/"+db_name
db = create_engine(db_string)

Session = sessionmaker(db)
session = Session()
Base.metadata.create_all(db)

vendors = import_vendors()


def test_insert_vendors():
    # Insert
    for vendor in vendors:
        session.add(vendor)
        session.commit()


def test_read_vendors():
    # Read
    vendors = session.query(Vendor)
    for vendor in vendors:
        print(vendor)


def test_update_vendors():
    # Update

    for vendor in vendors:
        vendor.name = vendor.name + ":Test-Update"
        session.commit()

    test_read_vendors()


def test_delete_vendors():
    # Delete
    for vendor in vendors:
        session.delete(vendor)
        session.commit()
