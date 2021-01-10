#!/usr/bin/python

import utils
# Defines class(es) pertaining to an organization.

class Organization:

    name=""
    id=""
    properties = {}

    def __init__(self, string_type, name_or_id_string):
        if string_type.upper() == 'NAME':
            self.name = name_or_id_string
            self.__get_id_from_name()
        elif string_type.upper() == 'ID':
            self.id = name_or_id_string
            utils.quit("ID to Name translation not yet implemented.")
        else:
            utils.quit("Unknown string type.  Has to be 'Name' or 'Id'")

        return

    def __get_id_from_name(self):
        # set up the API for correct org
        set_up = False
        for organization in utils.global_args.myorgs['orgs']:
            org_name = str(organization['name'])
            if self.name.upper() in org_name.upper():
                if organization['env'] == utils.global_args.env:
                    utils.d_print(5, "Org: ", organization)
                    self.properties = organization
                    self.id = organization['orgid']
                    set_up = True
                break

        if set_up == False:
            print (organization)
            utils.d_print(0, "Organization [", utils.global_args.client, "] not found in the myorgs.json file.")
            utils.quit("")    

        return self.id

    def get_name(self):
        return self.name

    def get_id(self):
        return self.id

    def get_properties(self):
        x = {}
        x['company_prefixes'] = self.properties["companyPrefixes"]
        x['hq_gln'] = self.properties["headQuartersGLN"]
        return x
