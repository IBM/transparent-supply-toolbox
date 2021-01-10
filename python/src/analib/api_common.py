#!/usr/bin/python

import json
import requests
import sys
import time
import utils

# make a post request
class PostRequest:
    MAX_ATTEMPTS = 5
    debug_level = 3

    def __init__(self, post_url, post_data, post_header, debug_level):
        self.post_url = post_url
        self.post_data = post_data
        self.post_header = post_header
        self.debug_level = debug_level
        return

    # make a post request
    def execute(self):
        attempts = 0

        # for SSL Errors, allow 5 attempts. For other exceptions, no additional attempts.
        while attempts < self.MAX_ATTEMPTS:
            try:
                utils.d_print(self.debug_level+3, "POST", "URL=", self.post_url, "DATA=", self.post_data, "HEADER=", self.post_header)
                r = requests.post(self.post_url, data=self.post_data, headers=self.post_header)
                utils.d_print(self.debug_level+3, "POST_RETURN", "r.encoding=", r.encoding, "r.status_code=", r.status_code)
                # we don't need to be in the loop. we had a success.
                break
            except requests.exceptions.SSLError:
                exceptionInfo = sys.exc_info()
                utils.d_print(2, "#### SSL Error Exception Occurred", exceptionInfo)
                attempts += 1
                if attempts >= self.MAX_ATTEMPTS:
                    utils.d_print(1, "SSL Exception occured more than 5 times during a single request!.  Quitting.")
                    utils.quit("EXIT.")
            else:
                exceptionInfo = sys.exc_info()
                print ("Exception Occurred:", exceptionInfo)
                utils.quit('!')
            utils.d_print(self.debug_level+3, "ATTEMPTS: ", attempts)
        return r


# make a get request
class GetRequest:
    MAX_ATTEMPTS = 5
    debug_level = 3

    def __init__(self, get_url, get_params, get_header, debug_level):
        self.get_url = get_url
        self.get_params = get_params
        self.get_header = get_header
        self.debug_level = debug_level
        return

    # make a post request
    def execute(self):
        attempts = 0

        # for SSL Errors, allow 5 attempts. For other exceptions, no additional attempts.
        while attempts < self.MAX_ATTEMPTS:
            try:
                utils.d_print(self.debug_level+3, "GET", "URL=", self.get_url, "PARAMS=", self.get_params, "HEADER=", self.get_header)
                r = requests.get(self.get_url, params=self.get_params, headers=self.get_header)
                utils.d_print(self.debug_level+3, "GET_RETURN", "r.encoding=", r.encoding, "r.status_code=", r.status_code)
                # we don't need to be in the loop. we had a success.
                break
            except requests.exceptions.SSLError:
                exceptionInfo = sys.exc_info()
                utils.d_print(2, "#### SSL Error Exception Occurred", exceptionInfo)
                attempts += 1
                if attempts >= self.MAX_ATTEMPTS:
                    utils.d_print(1, "SSL Exception occured more than 5 times during a single request!.  Quitting.")
                    utils.quit("EXIT.")
            else:
                exceptionInfo = sys.exc_info()
                print ("Exception Occurred:", exceptionInfo)
                utils.quit('!')
            utils.d_print(self.debug_level+3, "ATTEMPTS: ", attempts)
        return r


# authenticate using an api_key.  usually, this object will be kept alive during the
# life of api_inbound or api_outbound objects
class Authenticate:

    current_iam_token = None
    current_service_token = None

    api_key = ""
    org_id = ""
    env = "dev"
    config = {}
    debug_level = 3
    IAM_URL = "https://iam.ng.bluemix.net/oidc/token"
    IDENTITY_PROXY = ""

    # initialize with api_key, org_id and env
    #  env = "dev" or "staging" or "integration". NEVER "prod".
    def __init__(self, debug_level, org_id, env):
        self.org_id = org_id
        self.env = env
        self.debug_level = debug_level

        if self.env == "prod":
            utils.d_print(1, "env can never be prod")
            utils.quit("")

        #        self.IDENTITY_PROXY = utils.global_args.config['urls']['identity-proxy'][self.env] + self.org_id
        self.IDENTITY_PROXY = utils.global_args.config['urls']['hosts'][self.env] + utils.global_args.config['urls']['identity-proxy'][self.env] + self.org_id



        # if this is one of mr orgs, get the API key.
        self.__org_id_in_my_orgs()

        # keep a token ready
        # get_token() logic will work if there were a token (self.token is not None)
        # so, during init, we call __acquire_token() directly.
        self.__acquire_token()

        return

    # compute if the given org_id is one of my orgs
    def __org_id_in_my_orgs(self):
        ret_val = False
        for my_org in utils.global_args.myorgs['orgs']:
            if self.org_id == my_org['orgid']:
                self.api_key = my_org['apikey']
                utils.d_print(self.debug_level, "# MY ORG", my_org['name'])
                ret_val = True
                break
        if ret_val == False:
            utils.d_print(self.debug_level, "# NOT MY ORG", "")
        return ret_val


    # get cloud IAM Token:
    # curl -X POST --header "Content-Type: application/x-www-form-urlencoded" 
    #  --data "grant_type=urn:ibm:params:oauth:grant-type:apikey" 
    #  --data "apikey=<API_KEY>" https://iam.ng.bluemix.net/oidc/token
    def __acquire_cloud_iam_token(self):
        utils.d_print(self.debug_level+2, "IAM:", "ENTER")        
        post_header = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        post_data = {
            "grant_type" : "urn:ibm:params:oauth:grant-type:apikey",
            "apikey" : self.api_key
        }
        post_url = self.IAM_URL
        p = PostRequest(post_url, post_data, post_header, 3)
        r = p.execute()
        #r = self.__make_post_request(post_url, post_data, post_header)
        utils.d_print(self.debug_level+2, "IAM: EXIT", "r.text=", r.text, "r.headers=", r.headers)
        return r

    # env refers to prod, integration or dev
    # don't allow prod.
    #    curl -X POST -H 'Content-Type: ' -d 'IAM_RESP_BODY'
    #       https://fs-identity-proxy-integration.mybluemix.net/exchange_token/v1/organization/{IntegrationOrganizationId}
    def __acquire_service_token(self, iam_token):
        utils.d_print(self.debug_level+2, "Service Token","ENTER")

        post_header = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        post_data = json.loads(iam_token.text)
        post_url = self.IDENTITY_PROXY

        p = PostRequest(post_url, post_data, post_header, 3)
        r = p.execute()

        utils.d_print(self.debug_level+2, "Service Token:", "r.text=", utils.color.make_color('BLUE',r.text), "r.headers=", r.headers)
        try:
            x = r.json()
        except ValueError:
            utils.d_print(self.debug_level+2, "Did not receive a JSON in response: ", r.text)
            return x

        utils.d_print(self.debug_level+2, "EXIT: Token:", x)
        return x

    # get service token
    def __acquire_token(self):
        self.current_iam_token = self.__acquire_cloud_iam_token()
        utils.d_print(self.debug_level+1, "IAM_Token Object (text):", self.current_iam_token.text)
        service_token = self.__acquire_service_token(self.current_iam_token)
        utils.d_print(self.debug_level+1, "Service Token Object", service_token)
        self.current_service_token = service_token
        utils.d_print(self.debug_level+1, "EXIT", self.current_service_token)
        return service_token

    # check and return if the current token expired
    def __token_expired(self):
        time_since_epoch = int(time.time())
        cit = self.current_iam_token.json()
        if 'expiration' in cit:
            if int(cit['expiration']) < time_since_epoch:
                utils.d_print(self.debug_level, "TOKEN", "Expired")
                print ("Expired")
                return True
            else:
                utils.d_print(self.debug_level, "TOKEN", "Not Expired")
                #print "Not Expired"
                return False
        else:
            return True

    # authenticate and get the token
    def get_token(self):
        if self.__token_expired():
            
            if self.__org_id_in_my_orgs(): 
                # this is my org; acquire token
                self.__acquire_token()
            else:
                self.current_service_token = utils.global_args.master_tokens[self.env]

        return self.current_service_token


