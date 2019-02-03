#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import argparse
import json

from datetime import datetime
from secdb.aggregator import Aggregator
from secdb.vendors.factory import VendorFactory
from secdb.vendors.iex import IEX


def build_database(vendors):
    currencies = []
    exchanges = []
    symbols = []
    prices = []
    agg = Aggregator()

    # Using 4 loops, one for each dataset to be built.
    # Ensures that each dataset is fully built before building the next.
    for vendor in vendors:
        currencies.append(vendor.build_currency())
    agg.import_currencies(currencies)

    for vendor in vendors:
        exchanges.append(vendor.build_exchanges())
    agg.import_exchanges(exchanges)

    for vendor in vendors:
        symbols.append(vendor.build_symbols(agg.currencies, agg.exchanges))
    agg.import_symbols(symbols)

    # print(agg.symbols)

    for vendor in vendors:
        print(type(vendor))
        if (type(vendor) == IEX):
            prices.append(vendor.build_prices(agg.symbols))

    # agg.import_prices(prices)


def update_database(vendors):
    for vendor in vendors:
        vendor.update_currency()
        vendor.update_exchange()
        vendor.update_symbol()
        vendor.update_price()

    exit()


def import_vendors():
    vendors = []
    config_filename = "secdb/vendors.conf"

    # Load Configuration File
    with open(config_filename) as json_data_file:
        config = json.load(json_data_file)

    # Read Configuration Contents and create class object
    for vendor in config:
        factory = VendorFactory()
        vendor = factory(vendor, config)
        if vendor is not None:
            vendors.append(vendor)

    return vendors


def main():

    log_location="log/secdb.log"
    logging.basicConfig(filename=log_location, level=logging.DEBUG)
    now = datetime.utcnow()

    parser = argparse.ArgumentParser(
        description="Build and update a securities \
        master database"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--build", action="store_true", help="Build the database from scratch"
    )

    group.add_argument(
        "--update", action="store_true", help="Update the database with daily \
         values"
    )
    args = parser.parse_args()

    vendors = import_vendors()
    if (args.build):
        logging.info(str(now) + " Build option selected. Building database.")
        build_database(vendors)

    elif (args.update):
        logging.info(str(now) + " Update option selected. Updating database.")
        # update_database(vendors)

    else:
        parser.print_help()
        exit()


if __name__ == "__main__":
    main()
