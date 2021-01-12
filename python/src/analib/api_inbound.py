#!/usr/bin/python

from analib import api_common as api_common
import utils

class APIInbound:
    debug_level = 3
    env = "staging"
    header_entitled_org = None

    def __init__(self, debug_level, org_id, env, header_entitled_org):
        self.env = env
        self.org_id = org_id
        self.debug_level = debug_level
        self.header_entitled_org = header_entitled_org

        self.a = api_common.Authenticate(self.debug_level, self.org_id, self.env)
        self.token = self.a.get_token()

        return

    # quit the program if inbound data rules Fail.
    def validate_inbound_data_rules(self):

        if self.env == "prod":
            # you can NEVER push an XML to prod.
            utils.d_print(1, "env can never be prod")
            utils.quit("Tried to push to PROD !")            
            return False

        if self.env == "sandbox":
            return False

        return True

    # push a given XML into IFT
    # you can NEVER push to prod 
    def push_xml(self, xml_data):
        utils.d_print(self.debug_level, "ENTER", "len(xml_data)", len(xml_data))
        
        self.validate_inbound_data_rules()
        
        utils.d_print(self.debug_level+1, "XMLData:", xml_data)
        auth_token = "Bearer " + self.token['onboarding_token']
        post_header = {
            "Authorization": auth_token,
            "Content-Type": "application/xml"
        }
        if self.header_entitled_org:
            post_header["IFT-Entitled-Orgs"] = self.header_entitled_org
            
        post_data = xml_data.encode('utf-8')
        post_url = utils.global_args.config['urls']['hosts'][self.env] + utils.global_args.config['urls']['inbound'][self.env]

        p = api_common.PostRequest(post_url, post_data, post_header, 4)
        r = p.execute()
        utils.d_print(self.debug_level, "EXIT", "Response Text:", utils.color.make_color('RED', r.text), "Response Headers:", r.headers)
        utils.d_print(0, "EXIT", "Response Text:", utils.color.make_color('RED', r.text))
        return 

