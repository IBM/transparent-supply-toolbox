
#!/usr/bin/python

import json
import requests
import sys
import time
import utils

# Utility Class to convert back and forth from GS1 Formats
# Idea is not to keep state, but just to convert between
# formats as needed.
class GS1FormatUtil:

    def __init__(self):
        return

    # given a company prefix (list), a gtin and a lot number
    # generate the epc_class format.
    def generate_epc_class(self, company_prefix_list, gtin, lot):
        gtin_str = str(gtin)
        utils.d_print(5, "IS DIGIT: ", gtin_str.isdigit())
        if gtin_str.isdigit():
            # this is a pure GTIN
            prefix_str = ''
            ret_str = 'urn:epc:class:lgtin:'
            for company_prefix in company_prefix_list:
                prefix_str = str(company_prefix)
                if prefix_str in gtin_str:
                    ret_str += prefix_str + '.'
                    break
            utils.d_print(5, "gtin_str: ", gtin_str)
            utils.d_print(5, "prefix_str: ", prefix_str)

            indicator, itemref = gtin_str[:-1].split(prefix_str)
            ret_str += indicator + itemref + '.'
            ret_str += lot
        else:
            # we have an IFT id
            prefix_itemref = gtin_str.split(':class:')[1]
            ret_str = 'urn:ibm:ift:product:lot:class:' + \
                prefix_itemref + '.' + str(lot)
        utils.d_print(5, "GTIN, Lot, EPC Class: ", gtin, lot, ret_str)
        return ret_str