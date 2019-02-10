from secdb.currency import Currency
from sqlalchemy import create_engine
from secdb.currency import Base
from sqlalchemy.orm import sessionmaker


def test_create_currency():
    db_host = "localhost"
    db_user = "postgres"
    db_pass = ""
    db_name = "securities_master"

    db_string = "postgresql://"+db_user+":"+db_pass+"@"+db_host+"/"+db_name
    db = create_engine(db_string)

    Session = sessionmaker(db)
    session = Session()
    Base.metadata.create_all(db)

    # Create
    aud = Currency(
        code='AUD',
        num=36,
        minor_unit=2,
        name='Australian Dollar'
    )

    session.add(aud)
    session.commit()

    # Read
    currencies = session.query(Currency)
    for currency in currencies:
        print(currency)

    # Update
    aud.name = "Non-Australian Dollar"
    session.commit()

    # Read
    currencies = session.query(Currency)
    for currency in currencies:
        print(currency)

    # Delete
    session.delete(aud)
    session.commit()
