#!/usr/bin/python

import utils
import organization

from analib import api_outbound

class NativeAdapter:
    types = ['Facilities', 'Products', 'Events', 'Payloads']

    # a few stats are maintained
    processed = {}    # these are the numbers processed from the given spreadsheet
    built = {}        # Adapter will allow you to build additional events, payloads, facilities or products
    api_outbound = None
    org_id = None
    cached_locations = None
    cached_products = None

    # init function
    def __init__(self):
        for t in self.types:
            self.processed[t] = 0
            self.built[t] = []    # array per type holds any new manufactured ones
        
        # create and store an outbound_api in our object
        org = organization.Organization("Name", utils.global_args.client)
        self.org_id = org.get_id()
        self.api_outbound = api_outbound.APIOutbound(5, self.org_id, utils.global_args.env)
        return

    # this order should match the order in excel sheet
    # F_REG_GLN = 0, 
    # F_GLN = 1, 
    # F_NAME = 2, 
    # F_CITY = 3, 
    # F_STATE = 4 (Optional)
    # F_POSTALCODE = 5 (Optional), 
    # F_COUNTRYCODE = 6, 
    # F_PRNAME = 7, 
    # F_PRCODE = 8
    # F_SA_1 = 9 (Optional), 
    # F_SA_2 = 10 (Optional)
    def convert_facility_row(self, b_row):
        # dummy operation in native adapter
        self.increment_processed_count('Facilities')
        return b_row

    # P_ITEM_DESC = 0, 
    # P_GTIN = 1  : https://github.com/IBM/IFT-Developer-Zone/wiki/doc-IBMFoodTrust-ID-(identifiers)
    # P_SKU = 2, 
    # P_SENT_GLN = 3 (Corporate Identity GLN can be used), 
    # P_RECV_GLN = 4 (Optional)
    def convert_product_row(self, b_row):
        # dummy operation in native adapter
        self.increment_processed_count('Products')
        return b_row

    # this order should match the order in excel sheet
    # EV_TYPE = 0, 
    # EV_TIME = 1, 
    # EV_ID = 2, 
    # EV_INPUT_TYPE = 3, 
    # EV_INPUT = 4
    # EV_OUTPUT_TYPE = 5, 
    # EV_OUTPUT = 6
    # EV_BIZSTEP = 7           ## LIST OF BIZSTEPS that are native. ????
    # EV_BIZLOC = 8
    # EV_SRC = 9
    # EV_DEST = 10
    # EV_BIZ_TXN_TYPE_LIST = 11   ## POs...  -- need to write the code to put in biztxn.
    def convert_event_row(self, b_row):
        # dummy operation in native adapter
        self.increment_processed_count('Events')
        return b_row

    # PYLD_ID = 0   -- https://github.com/IBM/IFT-Developer-Zone/wiki/Payload-Data
    # PYLD_TIME = 1
    # PYLD_CONTENT_TYPE = 2
    # PYLD_URI = 3
    # PYLD_ATTACH_TYPE = 4
    # PYLD_ATTACH = 5
    # PYLD_TITLE = 6
    # PYLD_PYLD = 7
    def convert_payload_row(self, b_row):
        # dummy operation in native adapter
        self.increment_processed_count('Payloads')
        return b_row

    # increment the count of the processed
    def increment_processed_count(self, type):
        self.processed[type] += 1

    # get the count of the processed
    def get_processed_count(self, type):
        return self.processed[type]

    # returns the number of built 
    def get_built_count(self, type):
        if type in self.built:
            return len(self.built[type])
        else:
            utils.d_print(0, "Unknown Type. ", "Ignoring.")
            return 0

    # should return an array;
    # each element of the array will be an array of values
    def get_built_data(self, type):
        if type in self.built:
            return self.built[type]
        else:
            utils.d_print(0, "Unknown Type. ", "Ignoring.")
            return []

    # print the summary of statistics
    def print_summary(self):
        fr = ['Type', 'Processed', 'Built']
        t_count = {}
        for t in self.types:
            t_count[t] = [self.processed[t], len(self.built[t])]

        # print as a table
        st = utils.StatsTable()
        st.pretty_table_output(fr, t_count, alternate_color=True)
        return

    # create a bizstep as per BTS requirements.
    # use the 'http://...' prefix if not standard.
    # currently uses the client name as given in the command line args
    def make_bizstep(bizstep):
        ret_val = ''
        if bizstep in utils.global_args.gs1_bizsteps["bizstep"]:
            ret_val = bizstep
        else:
            ret_val = "http://" + utils.global_args.client + ".com/biz_step_name/" + bizstep
        return ret_val
    
    # check if a location exists in the BTS system
    # you can check with a location ID
    def location_exists(self, given_location_id, try_cached):
        loc_exists = False
        loc_array = None

        utils.d_print(4, "(given_location_id): ", given_location_id)

        try:

            # first check if we can try the cached array
            if not (try_cached and self.cached_locations):
                # if try_cached is set to false OR if the cached_locations are empty, then refresh.
                self.cached_locations = self.api_outbound.get_locations(self.org_id, [], [])

            loc_array = self.cached_locations

            print (loc_array)
            for location in loc_array:
                if given_location_id == location['id']:
                    loc_exists = True

            utils.d_print(1, "loc_exists: ", loc_exists)

        except:
            utils.print_exception(1)

        return loc_exists

    # check if a product exists in the BTS system
    # you can check with a location ID or a location description
    # check_type should be 'id' or 'description'
    def product_exists(self, check_type, check_value, try_cached):
        product_exists = False
        product_array = None

        utils.d_print(4, "(check_type, check_value): ", check_type, check_value)

        try:

            # first check if we can try the cached array
            if not (try_cached and self.cached_products):
                # if try_cached is set to false OR if the cached_locations are empty, then refresh with all products
                self.cached_products = self.api_outbound.get_products(self.org_id, None, None, None)

            product_array = self.cached_products

            for product in product_array:
#                if not isinstance(product, dict):
#                    continue
                if check_type == 'id':
                    if product['id'] == check_value:
                        product_exists = True
                elif check_type == 'description':
                    if product['description'] == check_value:
                        product_exists = True
                else:
                    utils.d_print(1, "Uknown Checktype", check_type, " Val: ", check_value)

            utils.d_print(1, "product_exists: ", product_exists)

        except:
            utils.print_exception(1)

        return product_exists
