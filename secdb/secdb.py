#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import logging
import argparse
import configparser

from datetime import datetime
from aggregator import Aggregator
from vendors.factory import VendorFactory


def build_database(vendor):
    # con = database.connect()
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

    # for vendor in vendors:
    # 	prices.append(vendor.build_price(agg.symbols))

    # agg.import_prices(prices)


def update_database():
    for vendor in vendors:
        vendor.update_currency()
        vendor.update_exchange()
        vendor.update_symbol()
        vendor.update_price()

    exit()


def help():
    print("Usage:")
    print("secdb --build")
    print("secdb --update")


def import_vendors():
    vendors = []
    config_filename = "vendors.conf"

    # Load Configuration File
    config = configparser.RawConfigParser()
    config.read(config_filename)

    # Read Configuration Contents
    for vendor in config.sections():
        factory = VendorFactory()
        vendor = factory(vendor, config)
        if vendor is not None:
            vendors.append(vendor)

            # vendor = Vendor.factory(vendor, config)
            # if vendor is not None:
            # 	vendors.append( vendor )

    return vendors


def main():
    pass


if __name__ == "__main__":
    """
    parser = argparse.ArgumentParser(description='Create a ArcHydro schema')
    parser.add_argument('--workspace', metavar='path', required=True,
                        help='the path to workspace')
    parser.add_argument('--schema', metavar='path', required=True,
                        help='path to schema')
    parser.add_argument('--dem', metavar='path', required=True,
                        help='path to dem')
    args = parser.parse_args()
    main(workspace=args.workspace, schema=args.schema, dem=args.dem)
    """

    arg = ""
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        now = datetime.utcnow()

    logging.basicConfig(filename="../log/secdb.log", level=logging.DEBUG)
    vendors = import_vendors()
    now = datetime.utcnow()

    if arg == "--build":
        logging.info(str(now) + " Build option selected. Building database.")
        build_database(vendors)

    elif arg == "--update":
        logging.info(str(now) + " Update option selected. Updating database.")
        # update_database()

    elif arg == "--help" or arg == "--h":
        help()
    else:
        print("Invalid argument.")
        help()
        exit()
