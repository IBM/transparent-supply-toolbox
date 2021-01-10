#!/usr/bin/python

import utils
import organization

from adapters.eprov_adapter_v2 import EProvenanceAdapter
from adapters.native_adapter import NativeAdapter
from excel_input import ExcelInput


def data_input_parse_args():

    # parse and print arguments
    utils.parse_arguments()

    if utils.global_args.mode == 'stats':
        utils.quit('stats mode not supported in data_input program; only input mode supported')
    if utils.global_args.mode == 'output':
        utils.quit('output mode not supported in data_input program; only input mode supported')

    if utils.global_args.inputxls == "" and utils.global_args.inputxml == "":
        utils.quit('both input excel file and xml file cannot be empty')


def push_xls(xls_filename):
    #m_adapter = EProvenanceAdapter()
    m_adapter = NativeAdapter()

    ei = ExcelInput(xls_filename, m_adapter)

    ei.push_to_bts()

    m_adapter.print_summary()

    return

# main function
def main():

    # parse arguments
    data_input_parse_args()

    # push an excel file
    push_xls(utils.global_args.inputxls)
    return

# invoke main function
main()