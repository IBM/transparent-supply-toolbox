
# Utilities for parsing, debugging, printing etc.

import argparse
import json
import os
import sys
import inspect
import linecache
import xlsxwriter

from pprint import pprint
from prettytable import PrettyTable


# print d_print( DEBUG_LEVEL, CONTEXT_STRING, VAR # ARGUMENTS..)
def d_print(*pargs):
    if len(pargs) <= 2 :
        print ("#DEBUG: Too few arguments to d_print function. At least 3 are needed: d_print( DEBUG_LEVEL, CONTEXT_STRING, VAR # ARGUMENTS...)")
        print (pargs[0], pargs[1])
        return
        
    # check if this print leve is greater than debug level
    print_level = pargs[0]
    if print_level > global_args.debug_level:
        return

    # get the context
    frame = inspect.currentframe()
    caller_frame = frame.f_back
    info = inspect.getframeinfo(caller_frame)

    # finish parsing pargs and create strings
    context_str = pargs[1]
    pargs_str = " ".join((map(lambda x: str(x), pargs[2:])))

    # create the message that includes context
    mesg_to_write = '[' + str(info.filename) + '|'\
                    + 'lineno:' + str(info.lineno) + '|'   \
                    + 'function:' + str(info.function) \
                    + '] : ' + context_str + ' ' + pargs_str + '\n'
    

    # finally, print
    print ("#DEBUG:" + mesg_to_write)

# pretty printing
def d_pprint(print_level, context_str, json_data): 
    if print_level <= global_args.debug_level:
        print ("#DEBUG: [", context_str, "]")
        pprint(json_data)


# dummy class (argument holder)
class Arguments:
    debug_level = 0
    simulate = False
    client = None
    hq_gln = None
    env = "sandbox"
    allowed_env_list = ['prod','sandbox','staging','dev','btseprov']
    orgsum = False
    gtinsum = False
    humanize = False
    eventsum = False
    mode = 'stats'  # can be 'stats' OR 'input' or 'output'
    outputxls = ""
    inputxls = ""
    inputxml = ""    
    isheets = []
    specific_rows = None
    header_entitled_org = ""
    config = {}
    myorgs = {}
    master_tokens = None
    CONFIG_FILE = "config/config.json"
    MY_ORGS_FILE = "config/myorgs.json"
    TOKEN_FILE = "config/tokens.json"
    GS1_BIZSTEPS_FILE = "config/gs1BizSteps.json"
    # this is the path to the BTSToolBox directory.
    BASE_PATH_DIR = ''

    def __init__(self):
        return

    def __repr__(self):
        pd = self._make_dict()
        pprint(pd)
        return json.dumps(pd)

    def __str__(self):
        pd = self._make_dict()
        pprint(pd)
        return json.dumps(pd)

    def _make_dict(self):
        print_dict = {}
        print_dict['debug_level'] = self.debug_level
        print_dict['simulate'] = self.simulate
        print_dict['client'] = self.client
        print_dict['env'] = self.env
        print_dict['orgsum'] = self.orgsum
        print_dict['gtinsum'] = self.gtinsum
        print_dict['eventsum'] = self.eventsum
        print_dict['outputxls'] = self.outputxls
        print_dict['mode'] = self.mode
        print_dict['orgfile'] = self.MY_ORGS_FILE
        print_dict['inputxls'] = self.inputxls
        print_dict['inputxml'] = self.inputxml
        print_dict['isheets'] = ' '.join(map(str, self.isheets))
        print_dict['headerentitleorg'] = self.header_entitled_org
        return print_dict
    
    # print all arguments as table
    def print_table(self):

        # args_table -> a_table
        a_first_row = ["Argument/Parameter", "Value"]
        a_first_row.insert(0,'')

        a_table = PrettyTable(a_first_row)

        a_dict = global_args._make_dict()

        row_no = 1
        for key,val in a_dict.items():
            if key == 'simulate':
                val = color.make_color('RED', str(val))
            a_row = [ str(row_no), key, val ]
            a_table.add_row(a_row)
            row_no += 1

        print (a_table)
        '''
        # Make 'Critical' RED.
        if vd_item['summary'].lower().startswith('critical'):
        txt = "\033[31;43m" + vd_item['summary'] + "\033[0m"
        txt = "\033[31;43m" + vd_item['summary'] + "\033[0m"
        '''

        return
    def load_config(self):
        try:
            config_file = open(self.BASE_PATH_DIR + 'src/' + self.CONFIG_FILE)
            self.config = json.load(config_file)
        except:
            print_exception(1)
        d_pprint(2, "Global Config", self.config)
        return

    def load_myorgs(self):
        try:
            myorgs_file = open(self.BASE_PATH_DIR + 'src/' + self.MY_ORGS_FILE)
            self.myorgs = json.load(myorgs_file)
        except:
            print_exception(1)
        d_pprint(2, "MyOrgs", self.myorgs)
        return        

    def load_master_tokens(self):
        try:
            with open(self.BASE_PATH_DIR + 'src/' + self.TOKEN_FILE) as token_file:
                self.master_tokens = json.load(token_file)
                d_pprint(5, "Tokens", self.master_tokens)        
        except:
            print_exception(1)
        return        
    
    def load_gs1_bizsteps(self):
        try:
            bizsteps_file = open(self.BASE_PATH_DIR + 'src/' + self.GS1_BIZSTEPS_FILE)
            self.gs1_bizsteps = json.load(bizsteps_file)
        except:
            print_exception(1)
        d_pprint(7, "BizSteps", self.gs1_bizsteps)
        return
              


# this will be imported into other files
global_args = Arguments()

def commmon_init():

    global_args.load_config()
    global_args.load_myorgs()
    global_args.load_master_tokens()
    global_args.load_gs1_bizsteps()



# this is the initialization/set up function that needs to be invoked if it is not a command
# like use of one of the data input/output/stats programs.  [i.e., e.g., from a webserver]
def init_all(debug_level=1, env_zone='sandbox'):

    # parse the environment
    global_args.env = env_zone
    global_args.debug_level = debug_level
    global_args.simulate = False
    global_args.mode = 'output'
    #global_args.client = client_name

    d_pprint(3, "Arguments (@ init_all):", global_args)

    # this is the common init, whether we call from a command line or corporate and use as lib
    commmon_init()


# this is not a class method
def parse_arguments():

    parser = argparse.ArgumentParser()

    parser.add_argument("-dbg", "--dbg", type=int,
                        help="debug level ([0..9]: 0 = no debug) (9 = lots of output)")

    parser.add_argument("-s", "--simulate",
                        help="useful for debugging",
                        action="store_true")

    parser.add_argument("-o","--org", type=str, required=True,
                        help="org name | ALL ")

    parser.add_argument("-e", "--env", type=str, required=True,
                        help="IFT environment/zone (prod|sandbox|dev|btseprov)")

    parser.add_argument("-of", "--orgsfile", type=str, required=False,
                        help="Org. details file (name, prefixes, apikey, etc.)")

    # there are 3 main modes of operation
    # 1. data input mode
    # 2. data output/trace mode
    # 3. statistics mode [NEED ADMIN TOKEN FOR THIS]
    mgroup = parser.add_mutually_exclusive_group(required=True)
    mgroup.add_argument("-I", "--input",
                        help="data input mode",
                        action="store_true")

    mgroup.add_argument("-O", "--output",
                        help="data output mode",
                        action="store_true")

    mgroup.add_argument("-S", "--stats",
                        help="stats mode",
                        action="store_true")

    # ------ input parameters -----
    group_di = parser.add_argument_group('Data Input', 'Upload one or more XML files to the system as specific org')
    group_di.add_argument("-ixls", "--inputxls", type=str, help="spreadsheet containing all data to be inputed")
    group_di.add_argument("-ie", "--ievents", action="store_true", help="take in events from the spreadsheet")
    group_di.add_argument("-if", "--ifacilities", action="store_true", help="take in facilities from the spreadsheet")
    group_di.add_argument("-ip", "--iproducts", action="store_true", help="take in products from the spreadsheet")
    group_di.add_argument("-ipl", "--ipayloads", action="store_true", help="take in payloads from the spreadsheet")
    group_di.add_argument("-srows", "--srows", type=str, help="specific comma separated excel row numbers from the tab(s) to be pushed (same row numbers from all the chosen tabs are pushed)")
    group_di.add_argument("-heo", "--headerentitleorg", type=str, help="orgid of the org that is to be entitled")
    group_di.add_argument("-ixml", "--inputxml", type=str, help="pathname of the single xml file to be uploaded")
    group_di.add_argument("-hqgln", "--headquartersgln", type=str, help="use this as the head quarter GLN")

    #group_di.add_argument("-cf", "--create-facility", nargs=9, help="paramters to generate a facility", 
    #    metavar=('registering_party_gln', 'gln', 'city', 'state', 'countrycode', 'name', 'postalcode', 'party_role_name', 'party_role_code'))



    # ------ output parameters -----
    group_do = parser.add_argument_group('Data Output', 'Get output using Trace/Fresh/.. APIs.')



    # ------ stats related parameters -----
    group_stats = parser.add_argument_group('Statistics', 'Get stats for one or more orgs')
    group_stats.add_argument("-u", "--humanize",
                            help="metrics in human readable manner",
                            action="store_true")

    group_stats.add_argument("-oxls", "--outputxls", type=str,
                            help="Excel Output Filename")

    group_stats.add_argument("-sum", "--summary", 
                            help="All Orgs Summary",
                            action="store_true")

    group_stats.add_argument("-gtin", "--gtinsum",
                            help="GTIN Summary",
                            action="store_true")
    
    group_stats.add_argument("-esum", "--eventsum",
                            help="Event Summary for Organizations",
                            action="store_true")

    args = parser.parse_args()

    # do any processing of input args here
    # and return the processed args
    if args.dbg:
        global_args.debug_level = args.dbg
    global_args.simulate = args.simulate
    global_args.client = args.org         # parse the client name

    if args.input == True:
        global_args.mode = 'input'
    elif args.output == True:
        global_args.mode = 'output'
    else:
        global_args.mode = 'stats'

    # parse the environment
    global_args.env = args.env
    if args.env == "dev":
        quit('Dev env not yet supported')
    if args.env not in global_args.allowed_env_list:
        quit('Unknown Environment Specified.   Should be one of ' + '|'.join(global_args.allowed_env_list))

    if (args.summary or args.gtinsum or args.humanize or args.eventsum or args.outputxls):
        if args.stats == False:
            quit('[summary | gtinsum | humanize | eventsum | outputxls] should go along with stats option.')

    if args.orgsfile:
        global_args.MY_ORGS_FILE = args.orgsfile

    global_args.orgsum = args.summary
    global_args.gtinsum = args.gtinsum
    global_args.humanize = args.humanize
    global_args.eventsum = args.eventsum
    if args.outputxls != None:
        if args.outputxls != '':
            global_args.outputxls = args.outputxls

    if args.inputxls:
        global_args.inputxls = args.inputxls

    if args.inputxml:
        global_args.inputxml = args.inputxml

    if args.ifacilities:
        global_args.isheets.append('if')
    if args.iproducts:
        global_args.isheets.append('ip')        
    if args.ievents:
        global_args.isheets.append('ie')
    if args.ipayloads:
        global_args.isheets.append('ipl')

    if args.headerentitleorg:
        global_args.header_entitled_org = args.headerentitleorg

    if args.headquartersgln:
        global_args.hq_gln = args.headquartersgln

    if args.srows:
        global_args.specific_rows = args.srows
    else:
        global_args.specific_rows = None

    d_pprint(3, "Arguments (after command line overriding):", global_args)

    path_set = False
    # check for environment variables; these will also be stored in the args class
    if 'BTS_TOOLBOX_BASE_PATH_DIR' in os.environ:
        if os.environ['BTS_TOOLBOX_BASE_PATH_DIR']:
            if os.environ['BTS_TOOLBOX_BASE_PATH_DIR'] != '':
                global_args.BASE_PATH_DIR =os.environ['BTS_TOOLBOX_BASE_PATH_DIR']
                path_set = True

    if path_set == False:
        d_print(0, "ENVIRONMENT VAR NOT SET:", "Please set the environment variable BTS_TOOLBOX_BASE_PATH_DIR to the base path.")
        quit("Exit.")

    commmon_init()

    global_args.print_table()

    return

# uncomment this and run for testing
'''
# main
if __name__ == '__main__':
    parse_arguments()
    print global_args
'''

# global variable for displaying colors in bash
class ColorPalette:

    # URL:  http://misc.flogisoft.com/bash/tip_colors_and_formatting
    # 32 	Green 	
    # 33 	Yellow 	
    # 34 	Blue 	
    # 35 	Magenta 	
    # 36 	Cyan 	
    # 37 	Light gray 	
    # 90 	Dark gray 	
    # 91 	Light red 	
    # 92 	Light green 	
    # 93 	Light yellow 	
    # 94 	Light blue 	
    # 95 	Light magenta 	
    # 96 	Light cyan 	
    # 97 	White 	
    prefixes = {
        'RED'     : "\033[31m ",
        'GREEN'   : "\033[32m ",
        'YELLOW'  : "\033[33m ",
        'BLUE'    : "\033[34m ",
        'MAGENTA' : "\033[35m ",
        'CYAN'    : "\033[36m ",
    }

    postfix = " \033[0m"
    
    def __init__(self):
        return

    # make the string RED and return
    def make_color(self, color, s):
        color_u = color.upper()
        if color_u in self.prefixes:
            prefix = self.prefixes[color_u]
            return prefix + s + self.postfix
        else:
            return s
    
# instantiate for use from other files
color = ColorPalette()

def print_exception(terminate):
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print ('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
    if terminate:
        sys.exit(0)

def quit(s):
    print ("EXIT: %s" %(s))
    sys.exit(0)
        

EVENT_SUMMARY = 0
GTIN_SUMMARY = 1

class StatsTable:
    xlsx_output_filename = "client_metrics.xlsx"
    customize = EVENT_SUMMARY

    # used for xlsx output
    def __init__(self):
        return

    # xlsx output to the file
    def _xlsx_output(self, first_row, p_dict):
        
        try:
            # Open an Excel workbook
            workbook = xlsxwriter.Workbook(self.xlsx_output_filename)
            header_format = workbook.add_format(properties={'bold': True, 'align': 'center', 'size' : 14})
            normal_format = workbook.add_format(properties={'align': 'center', 'size' : 14})
            #alert_format = workbook.add_format(properties={'font_color': 'red'})

            # Create a sheet
            worksheet = workbook.add_worksheet('metrics')
            if self.customize == EVENT_SUMMARY:
                worksheet.set_column(0, 0, 30)
                n_columns = len(first_row)
                worksheet.set_column((n_columns - 2), (n_columns - 1), 30)

            # Write the headers
            column = 0
            row = 0
            for value in first_row:
                worksheet.write(row, column, str(value), header_format)
                column += 1
            
            column = 0
            row += 1

            # for each row that we want to print
            for key,val in sorted(p_dict.items()):
                # write the key
                worksheet.write(row, column, str(key))

                # if value is a list, loop
                if isinstance(val, list):
                    for value in val:
                        worksheet.write(row, column, str(value), normal_format)
                        column += 1
                else:
                    worksheet.write(row, column, str(value), normal_format)

                row += 1
                column = 0


            # Close the workbook
            workbook.close()

        except:
            print_exception(True)

    # output as pretty table
    def pretty_table_output(self, first_row, p_dict, alternate_color=True):
        print_table_from_dict(first_row, p_dict, alternate_color)

    # output as xls
    def xls_table_output(self, first_row, p_dict, xlsx_output_filename, customize):
        self.xlsx_output_filename = xlsx_output_filename
        self.customize = customize
        self._xlsx_output(first_row, p_dict)

# print a prettytable from a dictionary
# (where each key has value of same # of columns)
def print_table_from_dict(first_row, p_dict, alternate_color=True):

    def row_color(row):
        MAX_ROW_COLORS = 2
        if alternate_color == False:
            return 'BLACK'
        if row % MAX_ROW_COLORS:
            return 'CYAN'
        else:
            return 'BLACK'

    d_first_row = list(first_row)
    d_first_row.insert(0,'')

    d_table = PrettyTable(d_first_row)
#    d_table[first_row[1]] = "l"
    row_no = 1
    for key,val in sorted(p_dict.items()):    
#        print "key = ", key
#        print "val = ", val

        colored_row_no = color.make_color(row_color(row_no), str(row_no))
        colored_key = color.make_color(row_color(row_no), str(key))

        if isinstance(val, list):
            d_row = [colored_row_no]
            d_row.append(colored_key)
            for x in val:
                colored_x = color.make_color(row_color(row_no), str(x))
                d_row.append(colored_x)
        else:
            colored_val = color.make_color(row_color(row_no), str(val))
            d_row = [ colored_row_no, colored_key, colored_val ]    

        d_print(5,"D_ROW:", d_row)
        d_table.add_row(d_row)
        row_no += 1

    print (d_table)
