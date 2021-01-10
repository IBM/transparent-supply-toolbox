#!/usr/bin/python

# Example file that shows how the API outbound works.
#  queries for products of an organization and prints out all the lots for each product

import datetime
import json
import time
import utils
import pprint
import organization

from analib import api_outbound as api_outbound
from datetime import datetime

# we do not support input or stats more here.
def parse_args_and_setup():
    # parse and print arguments
    utils.parse_arguments()
    if utils.global_args.mode == 'stats':
        utils.quit('stats mode not supported in data_analytics program; only output mode supported')
    if utils.global_args.mode == 'input':
        utils.quit('input mode not supported in data_analytics program; only output mode supported')

    return

def print_products_and_lots():

    print( "##################  Printing Products and Lots: #################")

    # 1. get org id
    org = organization.Organization("Name", utils.global_args.client)
    org_id = org.get_id()

    # 2. get outboundAPI
    outbound_api = api_outbound.APIOutbound(5, org_id, utils.global_args.env)

    # 3. get products
    products = outbound_api.get_products(org_id, None, None, None)
    utils.d_pprint(2, "Products:", products)
    for p in products:
        if len(p) <= 0 or p == {} or p == []:
            continue
        fr = [p['id'], p['description']]
        pr_lots = {}
        # 4. get lots and serials
        lots = outbound_api.get_lots_and_serials([str(p['id'])])
        if len(lots) != 0:
            lot_count = 1
            for l in lots:
#                        print "---> ", str(p['id']), " ", str(p['description'])
#                        print "Lot:", l
                if str(lot_count) in pr_lots:
                    pr_lots[l['id']].append('')
                else:
                    pr_lots[l['id']] = ['']
                lot_count += 1
            # print as a table
            st = utils.StatsTable()
            st.pretty_table_output(fr, pr_lots, alternate_color=True)

# main function
def main():

    parse_args_and_setup()

    print_products_and_lots()

    return

# invoke main function
main()