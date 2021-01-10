#/usr/bin/python

import json
import sys
import utils
from analib import api_common as api_common


class APIOutbound:
    debug_level = 3
    env = "staging"
    org_id = None

    def __init__(self, debug_level, org_id, env):
        self.env = env
        self.org_id = org_id
        self.debug_level = debug_level

        # authenticate and get the token for all the requests
        self.a = api_common.Authenticate(self.debug_level, self.org_id, self.env)
        self.token = self.a.get_token()
        utils.d_print(6, "self.token: ", self.token)

        return
 

    # combine multiple pages of results
    # data_type_name is 'Products' or 'Locations' or...
    def __get_aggregated(self, get_url, get_params, get_header, data_type_name):
        utils.d_print(self.debug_level, "ENTER", get_url)
        quit = False
        sequence_no = 1
        results = None
        while quit == False:
            utils.d_print(4, "Seq no: ", sequence_no)
            p = api_common.GetRequest(get_url, get_params, get_header, 4)
            sequence_no += 1
            r = p.execute()
            utils.d_print(self.debug_level, "EXIT", "Response Text:", utils.color.make_color('RED', r.text), "Response Headers:", r.headers)
            y = eval(r.text)
            utils.d_print(3, data_type_name, ':', y)
            if results == None:
                results = y[data_type_name]
            else:
                #results.append(y[data_type_name])
                results = results + y[data_type_name]
            quit = True
            if 'next' in y:
                if y['next']['href'] != '' :
                    # form the next get request
                    get_params = {}
                    get_url = y['next']['href']
                    quit = False
        utils.d_print(self.debug_level, "EXIT", "")
        return results

    def get_locations(self, org_id, glns, party_role_codes):

        utils.d_print(self.debug_level, "ENTER", org_id, glns, party_role_codes)

        auth_token = "Bearer " + self.token['onboarding_token']
        get_header = {
            "Authorization": auth_token,
            "Content-Type": "application/xml"
        }
        get_params = {}
        get_params['org_id'] = self.org_id # we are passing self.org_id here
        get_params['location_id'] = [glns] 
        get_params['party_role_code'] = [party_role_codes]
        get_url = utils.global_args.config['urls']['hosts'][self.env] + utils.global_args.config['urls']['outbound']['locations']

        quit = False
        sequence_no = 1
        results_array = []
        while quit == False:
            utils.d_print(3, "Seq no: ", sequence_no)
            p = api_common.GetRequest(get_url, get_params, get_header, 4)
            sequence_no += 1
            r = p.execute()
            utils.d_print(self.debug_level, "EXIT", "Response Text:", utils.color.make_color('RED', r.text), "Response Headers:", r.headers)
            y = eval(r.text)
            utils.d_print(3, "Locs (y): ", y)
            #results_array.append(y['locations'])
            results_array = results_array + y['locations']
            quit = True
            if 'next' in y:
                if y['next']['href'] != '' :
                    # form the next get request
                    get_params = {}
                    get_url = y['next']['href']
                    quit = False

        return results_array

    def get_products(self, org_id, description, lot_or_serial_ids, product_ids):

        utils.d_print(self.debug_level, "ENTER", org_id)

        auth_token = "Bearer " + self.token['onboarding_token']
        get_header = {
            "Authorization": auth_token,
            "Content-Type": "application/xml"
        }
        get_params = {}
        get_params['org_id'] = self.org_id
        get_params['description'] = description
        get_params['lot_or_serial_id'] = lot_or_serial_ids
        get_params['product_id'] = product_ids

        get_url = utils.global_args.config['urls']['hosts'][self.env] + utils.global_args.config['urls']['outbound']['products']

        products = self.__get_aggregated(get_url, get_params, get_header, 'products')

        return products

    def get_lots_and_serials(self, product_id):

        utils.d_print(self.debug_level, "ENTER", product_id)

        auth_token = "Bearer " + self.token['onboarding_token']
        get_header = {
            "Authorization": auth_token,
            "Content-Type": "application/xml"
        }
        get_params = {}
        get_params['product_id'] = product_id
        get_url = utils.global_args.config['urls']['hosts'][self.env] + utils.global_args.config['urls']['outbound']['lots_and_serials']

        lots_and_serials = self.__get_aggregated(get_url, get_params, get_header, 'lots_and_serials')

        return lots_and_serials


    def get_consumer_trace(self, epc_id):

        utils.d_print(self.debug_level, "ENTER", epc_id)

        auth_token = "Bearer " + self.token['onboarding_token']
        get_header = {
            "Authorization": auth_token,
            "Content-Type": "application/xml",
            "x-apicache-bypass" : "true"
        }
        get_params = {}
        get_url = utils.global_args.config['urls']['hosts'][self.env] + utils.global_args.config['urls']['outbound']['trace_consumer']
        get_url = get_url.replace('{epc_id}', epc_id)

        p = api_common.GetRequest(get_url, get_params, get_header, 4)
        r = p.execute()
        utils.d_print(self.debug_level, "EXIT", "Response Text:", utils.color.make_color('RED', r.text), "Response Headers:", r.headers)

        consumer_trace = eval(r.text)
        return consumer_trace

    def get_documents(self, docs_args):

        utils.d_print(self.debug_level, "ENTER: ", docs_args)

        auth_token = "Bearer " + self.token['onboarding_token']
        post_header = {
            "Authorization": auth_token,
            "Content-Type": "application/json",
#            "x-apicache-bypass" : "true"
        }
        post_params = docs_args
        post_url = utils.global_args.config['urls']['hosts'][self.env] + '/ift/api/documents/v1/documents/search'

        p = api_common.PostRequest(post_url, post_params, post_header, 4)
        r = p.execute()
        utils.d_print(self.debug_level, "EXIT", "Response Text:", utils.color.make_color('RED', r.text), "Response Headers:", r.headers)

        docs_result = json.loads(r.text)
        return docs_result

