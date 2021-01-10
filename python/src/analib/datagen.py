#!/usr/bin/python

import json
import utils

# class that will contain common converstion functions
class CommonCoversions:

    def __init__(self):
        return

    # process and generate time
    def time_in_iso_format(self, given_time):
        # '2020-01-15:23:10' to '2013-06-08T14:58:56.591Z'
        x = given_time.split(':')
        if len(x) != 3:
            utils.d_print(0, "Input Time: ", given_time)
            utils.quit("Time not in required format!  Format: YYYY-MM-DD:HH:MM")
        iso_time = x[0] + 'T' + x[1] + ':' + x[2] + ':00.000Z'
        return iso_time

    


N_EVENT_PARAMS = 12

# represents an event
# current restrictions:
#   - not taking ILMDs
#   - right now we do not handle 'E' -- EPC case. (i.e., Serial Numbers)
#   - take in only inputEPCList OR inputQuantityList -- not both of them in excel
#
class Event:
    EVENT_HEADER_FILE = "analib/Ed_Event.xmlHdr"
    EVENT_HEADER = ""
    EVENT_FOOTER = "</EventList></EPCISBody></epcis:EPCISDocument>"
    event_type = ''
    event_params = {}
    xml_string = ""
    company_prefix_list = []
    headquarters_gln = ""

    # this order should match the order in excel sheet
    EV_TYPE = 0
    EV_TIME = 1
    EV_ID = 2
    EV_INPUT_TYPE = 3
    EV_INPUT = 4
    EV_OUTPUT_TYPE = 5
    EV_OUTPUT = 6
    EV_BIZSTEP = 7
    EV_BIZLOC = 8
    EV_SRC = 9
    EV_DEST = 10
    EV_BIZ_TXN_TYPE_LIST = 11

    # other parameters
    EV_DEFAULT_TIME_ZONE = '-06:00'

    # not taking ILMDs now

    # take in various event parameters
    def __init__(self, org_params, e_params):
        with open(self.EVENT_HEADER_FILE) as header_file:
            self.EVENT_HEADER = header_file.read()
            self.event_params = e_params
            self.company_prefix_list = org_params['company_prefixes']
            self.headquarters_gln = org_params['hq_gln']
            utils.d_print(4, "Company Prefix List: ", self.company_prefix_list)
        return
    
    def __add_attribute(self, name, value):
        utils.d_print(5, "Adding Attribute: ", name, ": ", value)
        self.xml_string += '<' + name + '>' + str(value) + '</' + name + '>'

    # process and generate time
    def __generate_time_in_iso_format(self, given_time):
        try:
            # '2020-01-15:23:10' to '2013-06-08T14:58:56.591Z'
            x = given_time.split(':')
            if len(x) != 3:
                utils.d_print(0, "Input Time: ", given_time)
                utils.quit("Time not in required format!  Format: YYYY-MM-DD:HH:MM")
            iso_time = x[0] + 'T' + x[1] + ':' + x[2] + ':00.000Z'
            return iso_time
        except:
            utils.print_exception(1)

    # convert a GLN to an EPC Format GLN
    # expects a GLN integer
    def __gln_2_epcgln(self, gln):
        try:
            return_str = "urn:epc:id:sgln:"

            for company_prefix in self.company_prefix_list:
                if str(company_prefix) in str(gln):
                    return_str += str(company_prefix) + '.'
                    break

            location_ref = str(gln).split(str(company_prefix))[1]
            return_str += location_ref[:-1]
            return_str += '.0'
            return return_str
        except:
            utils.print_exception(1)            

    # generate an EPC Class : GTIN, Lot
    def __generate_epc_class(self, gtin, lot):
        try:
            gtin_str = str(gtin)
            utils.d_print(8, "GTINisDigit: ", gtin_str.isdigit())
            if gtin_str.isdigit():
                # this is a pure GTIN
                prefix_str = ''
                ret_str = 'urn:epc:class:lgtin:'
                for company_prefix in self.company_prefix_list:
                    prefix_str = str(company_prefix)
                    if prefix_str in gtin_str:
                        ret_str += prefix_str + '.'
                        break
                utils.d_print(8, "gtin_str: ", gtin_str)
                utils.d_print(8, "prefix_str: ", prefix_str)

                indicator, itemref = gtin_str[:-1].split(prefix_str)
                ret_str += indicator + itemref + '.'
                ret_str += lot
            else:
                # we have an IFT id
                prefix_itemref = gtin_str.split(':class:')[1]
                ret_str = 'urn:ibm:ift:product:lot:class:' + prefix_itemref + '.' + str(lot)
            utils.d_print(5, "GTIN, Lot, EPC Class: ", gtin, lot, ret_str)
            return ret_str
        except:
            utils.print_exception(1)        

    # generate an EPC for a Serial Number
    def __generate_epc_serial(self, gtin_str, serial):
        try:
            return_str = ''
            if 'urn:ibm:ift:' in gtin_str:
                # we have an IFT id
                prefix_itemref = gtin_str.split(':class:')[1]
                return_str = 'urn:ibm:ift:product:serial:obj:' + prefix_itemref + '.' + str(serial)
            else:
                utils.quit("GS1 Serials not yet implemented.")
            return return_str
        except:
            utils.print_exception(1)

    # generate an EPC for a Logistic Unit
    def __generate_lu(self, lu_details):
        try:
            utils.d_print(7, "LU Gen", lu_details)
            return_str = '' 
            if 'lu' in lu_details:
                lud = lu_details['lu']
                if 'urn:ibm:ift:' in lud:
                    return_str = lud
                else:
                    utils.quit("GS1 LUs not yet implemented.")
            else:
                utils.d_print(7, "LU Generation: ", lu_details)
                utils.quit("'lu' key not present.")
            return return_str
        except:
            utils.print_exception(1)

    # process and generate quantity list
    def __generate_quantity_list(self, qty_list_name, qty_list):
        try:
            utils.d_print(7, "Gen Qty list: ", qty_list)
            self.xml_string += '<' + qty_list_name + '>'
            x = json.loads(qty_list)
            utils.d_print(8, "Qty List JSON String: ", x)
            for x_item in x:
                self.xml_string += '<quantityElement>'
                utils.d_print(7, "x_item[GTIN]: ", x_item['gtin'])
                utils.d_print(7, "x_item[LOT   ]: ", x_item['lot'])
                self.__add_attribute('epcClass', self.__generate_epc_class(x_item['gtin'], x_item['lot']))
                self.__add_attribute('quantity', x_item['qty'])
                self.__add_attribute('uom', x_item['uom'])
                self.xml_string += '</quantityElement>'
                utils.d_print(7, "XML_String:", self.xml_string)
            self.xml_string += '</' + qty_list_name + '>'
        except:
            utils.print_exception(1)
        return

    # loc_type is 'src' or 'destination'
    def __generate_src_dest(self, loc_type, gln):
        try:
            return_str = ''
                    
            if gln != None:
                return_str += '<' + loc_type + 'List>'
                return_str += '<' + loc_type + ' type="urn:epcglobal:cbv:sdt:owning_party">'

                if "urn:ibm:ift:location" in str(gln):
                    return_str += gln
                else:
                    return_str += self.__gln_2_epcgln(gln)
                
                return_str += '</' + loc_type + '>'
                return_str += '</' + loc_type + 'List>'

            return return_str
        except:
            utils.print_exception(1)
    # 
    def __generate_bizloc(self, gln):
        try:
            utils.d_print(7, "bizloc gln passed:", gln)
            return_str = '<bizLocation><id>'
            if "urn:ibm:ift:location" not in str(gln):
                return_str += self.__gln_2_epcgln(gln)
            else:
                return_str += gln
            return_str += '</id></bizLocation>'
            return return_str
        except:
            utils.print_exception(1)            

    # 
    def __generate_bizstep(self, bizstep):
        try:
            utils.d_print(7, "bizstep value passed:", bizstep)
            return_str = '<bizStep>'
            if "http:" not in bizstep:
                return_str += 'urn:epcglobal:cbv:bizstep:' + bizstep
            else:
                return_str += bizstep
            return_str += '</bizStep>'
            return return_str
        except:
            utils.print_exception(1)            

    # generates an EPC list
    def __generate_epc_list(self, epc_name, epc_serial_params):
        try:
            utils.d_print(7, "epc values:", epc_name, epc_serial_params)
            x = json.loads(epc_serial_params)
            return_str = '<' + epc_name + '>'
            for product_details in x:
                print (product_details)
                if 'gtin' in product_details:
                    gtin_str = product_details['gtin']
                    for serial_no in product_details['serial']:
                        return_str += '<epc>'
                        return_str +=  self.__generate_epc_serial(gtin_str, serial_no)
                        return_str += '</epc>'
                elif 'lu' in product_details:
                        return_str += '<epc>'
                        return_str +=  self.__generate_lu(product_details)
                        return_str += '</epc>'
                else:
                    utils.quit("Unknown key name (not gtin or lu) in EPC details")
            return_str += '</' + epc_name + '>'
            self.xml_string += return_str
            utils.d_print(7, "return_str: ", return_str)
        except:
            utils.print_exception(1)            

    # generates biz txns
    def __generate_biztxn_list(self, biz_txn_params):
        USE_GS1_TYPES = True  # for now, we will support only GS1 types
        try:
            utils.d_print(7, "biztxn params passed:", biz_txn_params)
            return_str = ""
            if biz_txn_params != None and biz_txn_params != "" :
                x = json.loads(biz_txn_params)
                embed_str = ""
                for biztxn in x:
                    if 'po' in biztxn:
                        if USE_GS1_TYPES:
                            embed_str += '<bizTransaction type= "urn:epcglobal:cbv:btt:po">'
                            # FORMAT: urn:epcglobal:cbv:bt:1234567890123:T1234 
                            embed_str += "urn:epcglobal:cbv:bt:" + self.headquarters_gln + ":" + biztxn['po']
                        else:
                            # urn:ibm:ift:bt:<Company Prefix>.<Location Reference>.<Transaction Id>
                            # Note that head quarters GLN here (and in the config file is not fully qualified)
                            # i.e., urn:ibm:ift:location:loc:21345589.HQ is represented as 21345589.HQ only
                            embed_str += '<bizTransaction>'
                            embed_str += "urn:ibm:ift:bt:" + self.headquarters_gln + "." + biztxn['po']
                        embed_str += "</bizTransaction>"
                    elif 'da' in biztxn:
                        if USE_GS1_TYPES:
                            embed_str += '<bizTransaction type= "urn:epcglobal:cbv:btt:desadv">'
                            # FORMAT: urn:epcglobal:cbv:bt:1234567890123:T1234 
                            embed_str += "urn:epcglobal:cbv:bt:" + self.headquarters_gln + ":" + biztxn['da']
                        else:
                            # urn:ibm:ift:bt:<Company Prefix>.<Location Reference>.<Transaction Id>
                            # Note that head quarters GLN here (and in the config file is not fully qualified)
                            # i.e., urn:ibm:ift:location:loc:21345589.HQ is represented as 21345589.HQ only
                            embed_str += '<bizTransaction>' # type=" + ' "urn:epcglobal:cbv:btt:desadv">'
                            embed_str += "urn:ibm:ift:bt:" + self.headquarters_gln + "." + biztxn['da']
                        embed_str += '</bizTransaction>'
                    elif 'prodorder' in biztxn:
                        if USE_GS1_TYPES:
                            embed_str += '<bizTransaction type= "urn:epcglobal:cbv:btt:prodorder">'
                            # FORMAT: urn:epcglobal:cbv:bt:1234567890123:T1234 
                            embed_str += "urn:epcglobal:cbv:bt:" + self.headquarters_gln + ":" + biztxn['prodorder']
                        else:
                            # urn:ibm:ift:bt:<Company Prefix>.<Location Reference>.<Transaction Id>
                            # Note that head quarters GLN here (and in the config file is not fully qualified)
                            # i.e., urn:ibm:ift:location:loc:21345589.HQ is represented as 21345589.HQ only
                            embed_str += '<bizTransaction>' # type=" + ' "urn:epcglobal:cbv:btt:prodorder">'
                            embed_str += "urn:ibm:ift:bt:" + self.headquarters_gln + "." + biztxn['prodorder']
                        embed_str += '</bizTransaction>'
                    else:
                        utils.d_print(2, "Unknown Biz Txn Type", biz_txn_params)

                if embed_str != "":
                    return_str = '<bizTransactionList>' + embed_str + '</bizTransactionList>'

            return return_str
        except:
            utils.print_exception(1)       
        return

    ####  Event Types Start Here ####

    # comission
    def __generate_com_xml(self):
        try:
            self.xml_string += "<ObjectEvent>"

            # convert time to required string and add
            self.__add_attribute('eventTime', self.__generate_time_in_iso_format(self.event_params[self.EV_TIME]))
            self.__add_attribute('eventTimeZoneOffset', self.EV_DEFAULT_TIME_ZONE)


            self.xml_string += "<baseExtension>"
            self.__add_attribute('eventID', self.event_params[self.EV_ID])
            self.xml_string += "</baseExtension>"

            self.__add_attribute('action', 'ADD')

            self.xml_string += self.__generate_bizstep(self.event_params[self.EV_BIZSTEP])
            self.xml_string += self.__generate_bizloc(self.event_params[self.EV_BIZLOC])

            if self.event_params[self.EV_OUTPUT_TYPE] == 'Q':
                self.__add_attribute('epcList', '')
            else:
                utils.quit("Add EPCs in Commission event to handle type 'E'")

            self.xml_string += "<extension>"

            if self.event_params[self.EV_OUTPUT_TYPE] == 'Q':
                self.__generate_quantity_list('quantityList', self.event_params[self.EV_OUTPUT])

            # add source and desination lists here
            self.xml_string += self.__generate_src_dest('source', self.event_params[self.EV_SRC])
            self.xml_string += self.__generate_src_dest('destination', self.event_params[self.EV_DEST])
            self.xml_string += "</extension>"

            # add biz txn documents here
            self.xml_string += self.__generate_biztxn_list(self.event_params[self.EV_BIZ_TXN_TYPE_LIST])

            self.xml_string += "</ObjectEvent>"

            utils.d_print(2, "## Commission: ", self.xml_string)
        except:
            utils.print_exception(1)
        return    

   # transformation
    def __generate_xfm_xml(self):
        try:
            self.xml_string += "<extension> <TransformationEvent>"
            self.__add_attribute('eventTime', self.__generate_time_in_iso_format(self.event_params[self.EV_TIME]))
            self.__add_attribute('eventTimeZoneOffset', self.EV_DEFAULT_TIME_ZONE)

            self.xml_string += "<baseExtension>"
            self.__add_attribute('eventID', self.event_params[self.EV_ID])
            self.xml_string += "</baseExtension>"

            self.xml_string += self.__generate_bizloc(self.event_params[self.EV_BIZLOC])
            self.xml_string += self.__generate_bizstep(self.event_params[self.EV_BIZSTEP])

            # input for transformation
            if self.event_params[self.EV_INPUT_TYPE] == 'Q':
                self.__generate_quantity_list('inputQuantityList', self.event_params[self.EV_INPUT])
            elif self.event_params[self.EV_INPUT_TYPE] == 'E':
                self.__generate_epc_list('inputEPCList', self.event_params[self.EV_INPUT])
            else:
                utils.quit('Unknown Input Type ' + self.event_params[self.EV_INPUT_TYPE])

            # output for transformation
            if self.event_params[self.EV_OUTPUT_TYPE] == 'Q':
                self.__generate_quantity_list('outputQuantityList', self.event_params[self.EV_OUTPUT])
            elif self.event_params[self.EV_OUTPUT_TYPE] == 'E':
                self.__generate_epc_list('outputEPCList', self.event_params[self.EV_OUTPUT])
            else:
                utils.quit('Unknown Output Type ' + self.event_params[self.EV_OUTPUT_TYPE])


            self.xml_string += "<extension>"
            self.xml_string += self.__generate_src_dest('source', self.event_params[self.EV_SRC])
            self.xml_string += self.__generate_src_dest('destination', self.event_params[self.EV_DEST])
            self.xml_string += "</extension>"

            # add biz txn documents here
            self.xml_string += self.__generate_biztxn_list(self.event_params[self.EV_BIZ_TXN_TYPE_LIST])

            self.xml_string += "</TransformationEvent></extension> "

            utils.d_print(2, "## Transformation: ", self.xml_string)        
        except:
            utils.print_exception(1)
        return

    # aggregation
    def __generate_agg_xml(self):
        try:

            self.xml_string += "<AggregationEvent>"
            self.__add_attribute('eventTime', self.__generate_time_in_iso_format(self.event_params[self.EV_TIME]))
            self.__add_attribute('eventTimeZoneOffset', self.EV_DEFAULT_TIME_ZONE)

            self.xml_string += "<baseExtension>"
            self.__add_attribute('eventID', self.event_params[self.EV_ID])
            self.xml_string += "</baseExtension>"

            self.xml_string += self.__generate_bizloc(self.event_params[self.EV_BIZLOC])

            # output is a pallet id etc., the parent
            # for now, only Logistic Units are supported as parents;  infact, only 1 logistic unit.

            x = json.loads(self.event_params[self.EV_OUTPUT])
            lu_details = x[0]
            self.__add_attribute('parentID',  self.__generate_lu(lu_details))

            if self.event_params[self.EV_INPUT_TYPE] == 'E':
                self.__generate_epc_list('childEPCs', self.event_params[self.EV_INPUT])
            elif self.event_params[self.EV_INPUT_TYPE] == 'Q':
                self.__add_attribute('childEPCs', '')
            else:
                utils.quit('Unknown Input Type ' + self.event_params[self.EV_INPUT_TYPE])

            self.__add_attribute('action', 'ADD')
            self.xml_string += self.__generate_bizstep(self.event_params[self.EV_BIZSTEP])

            self.xml_string += '<extension>'

            # generate the inputs, the children
            if self.event_params[self.EV_INPUT_TYPE] == 'Q':
                self.__generate_quantity_list('childQuantityList', self.event_params[self.EV_INPUT])

            self.xml_string += self.__generate_src_dest('source', self.event_params[self.EV_SRC])
            self.xml_string += self.__generate_src_dest('destination', self.event_params[self.EV_DEST])

            self.xml_string += '</extension>'

            # add biz txn documents here
            self.xml_string += self.__generate_biztxn_list(self.event_params[self.EV_BIZ_TXN_TYPE_LIST])

            self.xml_string += '</AggregationEvent>'

            utils.d_print(2, "## Aggregation: ", self.xml_string)        
        except:
            utils.print_exception(1)
        return

    # disaggregation
    def __generate_dag_xml(self):
        try:
            self.xml_string += "<AggregationEvent>"
            self.__add_attribute('eventTime', self.__generate_time_in_iso_format(self.event_params[self.EV_TIME]))
            self.__add_attribute('eventTimeZoneOffset', self.EV_DEFAULT_TIME_ZONE)

            self.xml_string += "<baseExtension>"
            self.__add_attribute('eventID', self.event_params[self.EV_ID])
            self.xml_string += "</baseExtension>"

            self.xml_string += self.__generate_bizloc(self.event_params[self.EV_BIZLOC])

            # output is a pallet id etc., the parent
            # for now, only Logistic Units are supported as parents;  infact, only 1 logistic unit.

            x = json.loads(self.event_params[self.EV_INPUT])
            lu_details = x[0]
            self.__add_attribute('parentID',  self.__generate_lu(lu_details))

            if self.event_params[self.EV_OUTPUT_TYPE] == 'E':
                self.__generate_epc_list('childEPCs', self.event_params[self.EV_OUTPUT])
            elif self.event_params[self.EV_OUTPUT_TYPE] == 'Q':
                self.__add_attribute('childEPCs', '')
            else:
                utils.quit('Unknown Input Type ' + self.event_params[self.EV_OUTPUT_TYPE])

            self.__add_attribute('action', 'DELETE')
            self.xml_string += self.__generate_bizstep(self.event_params[self.EV_BIZSTEP])

            self.xml_string += '<extension>'

            # generate the outputs, the children
            if self.event_params[self.EV_OUTPUT_TYPE] == 'Q':
                self.__generate_quantity_list('childQuantityList', self.event_params[self.EV_OUTPUT])

            self.xml_string += self.__generate_src_dest('source', self.event_params[self.EV_SRC])
            self.xml_string += self.__generate_src_dest('destination', self.event_params[self.EV_DEST])

            self.xml_string += '</extension>'

            # add biz txn documents here
            self.xml_string += self.__generate_biztxn_list(self.event_params[self.EV_BIZ_TXN_TYPE_LIST])

            self.xml_string += '</AggregationEvent>'

            utils.d_print(2, "## Disaggregation: ", self.xml_string)    
        except:
            utils.print_exception(1)             
        return

    # observation
    def __generate_obs_xml(self):
        try:
            self.xml_string += "<ObjectEvent>"
            self.__add_attribute('eventTime', self.__generate_time_in_iso_format(self.event_params[self.EV_TIME]))
            self.__add_attribute('eventTimeZoneOffset', self.EV_DEFAULT_TIME_ZONE)

            self.xml_string += "<baseExtension>"
            self.__add_attribute('eventID', self.event_params[self.EV_ID])
            self.xml_string += "</baseExtension>"

            self.xml_string += self.__generate_bizloc(self.event_params[self.EV_BIZLOC])
            self.xml_string += self.__generate_bizstep(self.event_params[self.EV_BIZSTEP])

            self.__add_attribute('action', 'OBSERVE')

            if self.event_params[self.EV_INPUT_TYPE] == 'E':
                self.__generate_epc_list('epcList', self.event_params[self.EV_INPUT])
            elif self.event_params[self.EV_INPUT_TYPE] == 'Q':
                self.__add_attribute('epcList', '')
            else:
                utils.quit('Unknown Input Type ' + self.event_params[self.EV_INPUT_TYPE])

            self.xml_string += '<extension>'

            # input for observation
            if self.event_params[self.EV_INPUT_TYPE] == 'Q':
                self.__generate_quantity_list('quantityList', self.event_params[self.EV_INPUT])
            elif self.event_params[self.EV_INPUT_TYPE] != 'E':
                utils.quit('Unknown Input Type ' + self.event_params[self.EV_INPUT_TYPE])
            
            self.xml_string += self.__generate_src_dest('source', self.event_params[self.EV_SRC])
            self.xml_string += self.__generate_src_dest('destination', self.event_params[self.EV_DEST])

            self.xml_string += '</extension>'

            # add biz txn documents here
            self.xml_string += self.__generate_biztxn_list(self.event_params[self.EV_BIZ_TXN_TYPE_LIST])

            self.xml_string += '</ObjectEvent>'

            utils.d_print(2, "## Observation: ", self.xml_string)        
        except:
            utils.print_exception(1)
        return

    def __generate_xml(self):

        self.xml_string = self.EVENT_HEADER

        print (self.event_params[self.EV_TYPE].upper() )
        if self.event_params[self.EV_TYPE].upper() == 'COMMISSION':
            self.__generate_com_xml()
        elif self.event_params[self.EV_TYPE].upper() == 'TRANSFORMATION':
            self.__generate_xfm_xml()
        elif self.event_params[self.EV_TYPE].upper() == 'AGGREGATION':
            self.__generate_agg_xml()
        elif self.event_params[self.EV_TYPE].upper() == 'DISAGGREGATION':
            self.__generate_dag_xml()
        elif self.event_params[self.EV_TYPE].upper() == 'OBSERVATION':
            self.__generate_obs_xml()
        else:
            utils.d_print(2, self.event_params[self.EV_TYPE], " not yet supported.")

        self.xml_string += self.EVENT_FOOTER

        utils.d_print(5, "Returning XML: ", self.xml_string)

        return self.xml_string

    def get_xml(self):
        return self.__generate_xml()

N_PRODUCT_PARAMS = 5

# represents a product
class Product:
    PRODUCT_HEADER_FILE = "analib/MD_Product.xmlHdr"
    PRODUCT_HEADER = ""
    PRODUCT_FOOTER = "</item_data_notification:itemDataNotificationMessage>"
    product_params = {}
    xml_string = ""

    # this order should match the order in excel sheet
    P_ITEM_DESC = 0
    P_GTIN = 1
    P_SKU = 2
    P_SENT_GLN = 3
    P_RECV_GLN = 4

    # take in various facility parameters
    def __init__(self, org_params, p_params):
        with open(self.PRODUCT_HEADER_FILE) as header_file:
            self.PRODUCT_HEADER = header_file.read()
            self.p_item_desc = p_params[self.P_ITEM_DESC]
            self.p_gtin = p_params[self.P_GTIN]
            self.p_sku = p_params[self.P_SKU]
            self.p_sent_gln = p_params[self.P_SENT_GLN]
            self.p_recv_gln = p_params[self.P_RECV_GLN]
        return
    
    def __add_attribute(self, name, value):
        self.xml_string += '<' + name + '>' + str(value) + '</' + name + '>'

    def __generate_xml(self):
        self.xml_string = self.PRODUCT_HEADER
        self.xml_string += '<tradeItemData>'

        self.xml_string += '<tradeItemDescription languageCode="en">'
        self.xml_string += self.p_item_desc
        self.xml_string += '</tradeItemDescription>'


        self.__add_attribute('gtin', self.p_gtin)
        self.__add_attribute('sku', self.p_sku)

        self.xml_string += '<dataSource>'
        self.__add_attribute('gln', self.p_sent_gln)
        self.xml_string += '</dataSource>'

        self.xml_string += '<dataRecipient>'
        self.__add_attribute('gln', self.p_recv_gln)
        self.xml_string += '</dataRecipient>'

        self.xml_string += '</tradeItemData>'
        self.xml_string += self.PRODUCT_FOOTER

        return self.xml_string

    def get_xml(self):
        return self.__generate_xml()

N_FACILITY_PARAMS = 11

# represents a facility
class Facility:
    FACILITY_HEADER_FILE = "analib/MD_Facility.xmlHdr"
    FACILITY_HEADER = ""
    FACILITY_FOOTER = "</basic_party_registration:basicPartyRegistrationMessage>"
    facility_params = {}
    xml_string = ""

    # this order should match the order in excel sheet
    F_REG_GLN = 0
    F_GLN = 1
    F_NAME = 2
    F_CITY = 3
    F_STATE = 4
    F_POSTALCODE = 5
    F_COUNTRYCODE = 6
    F_PRNAME = 7
    F_PRCODE = 8
    F_SA_1 = 9
    F_SA_2 = 10

    # take in various facility parameters
    def __init__(self, org_params, f_params):
        with open(self.FACILITY_HEADER_FILE) as header_file:
            self.FACILITY_HEADER = header_file.read()
            self.registering_party_gln = f_params[self.F_REG_GLN]
            self.gln = f_params[self.F_GLN]
            self.a_name = f_params[self.F_NAME]
            self.a_city = f_params[self.F_CITY]
            self.a_state = f_params[self.F_STATE]
            self.a_countrycode = f_params[self.F_COUNTRYCODE]
            self.a_postalcode = f_params[self.F_POSTALCODE]
            self.pr_name = f_params[self.F_PRNAME]
            self.pr_code = f_params[self.F_PRCODE]
            self.sa_1 = f_params[self.F_SA_1]
            self.sa_2 = f_params[self.F_SA_2]
            #print self.FACILITY_HEADER
        return
    
    def __add_attribute(self, name, value):
        self.xml_string += '<' + name + '>' + str(value) + '</' + name + '>'

    def __generate_xml(self):
        self.xml_string = self.FACILITY_HEADER
        self.xml_string += '<party>'

        # <!--MANDATORY: isPartyActive will be set to False, if a facility is closed etc.-->
        self.__add_attribute('isPartyActive', 'true')

        # <!--MANDATORY: Organization's corporate identity GLN-->
        self.__add_attribute('registeringParty', self.registering_party_gln)
        self.__add_attribute('gln', self.gln)

        # party address
        self.xml_string += '<partyAddress>'
        self.__add_attribute('city', self.a_city)
        self.__add_attribute('countryCode', self.a_countrycode)
        self.__add_attribute('name', self.a_name)
        self.__add_attribute('postalCode', self.a_postalcode)
        self.__add_attribute('state', self.a_state)
        self.xml_string += '</partyAddress>'        
        self.__add_attribute('streetAddressOne', self.sa_1)
        self.__add_attribute('streetAddressTwo', self.sa_2) 

        # party role code
        self.xml_string += '<partyRole>'
        self.__add_attribute('partyName', self.pr_name)
        self.__add_attribute('partyRoleCode', self.pr_code)
        self.xml_string += '</partyRole>'

        self.xml_string += '</party>'
        self.xml_string += self.FACILITY_FOOTER

        return self.xml_string

    def get_xml(self):
        return self.__generate_xml()


'''
  <payloadID>string</payloadID>
    <!--Mandatory: ID of this payload.-->
    <payloadTime>2018-09-28T21:49:45Z</payloadTime>
    <!--Optional: Timestamp for this payload message.-->
    <payloadContentType>application/json</payloadContentType>
    <!--Optional: http content type of payload - application/json -->
    <payloadTypeURI>string</payloadTypeURI>
    <!--Mandatory: URI for payload type - string or json triple or sensor -->
    <eventIDList>
      <eventID>eventID1</eventID>
      <eventID>eventID2</eventID>
    </eventIDList>
    <!--Optional: List of events with which this payload is associated.-->
    <epcList>
      <!--Zero or more epc elements of type: GTIN, LGTIN, SGTIN, SSCC -->
      <epc>urn:epc:id:sscc:0614141.0123456789</epc>
      <epc>urn:ibm:ift:product:serial:obj:0614141000000.107346.2016</epc>
    </epcList>
    <!--Optional: List of epcs with which this payload is associated.-->
    <locationList>
      <!--Location elements of type: EPC-SGLN or IBM Food Trust location-with-extension -->
      <location>urn:epc:id:sgln:0614141.00777.0</location>
      <location>urn:ibm:ift:location:extension:loc:1234567890123.store-123.toy-department</location>
    </locationList>
    <!--Optional: List of locations with which this payload is associated.-->
    <payload>string</payload>
    <!--Mandatory: payload - string or json triple or sensor -->
'''

N_PAYLOAD_PARAMS = 8

# represents a payload
class Payload:
    PAYLOAD_HEADER_FILE = "analib/Pld_Payload.xmlHdr"
    PAYLOAD_HEADER = ""
    PAYLOAD_FOOTER = "</payloadMessage></ift:payload>"
    payload_params = {}
    xml_string = ""

    # this order should match the order in excel sheet
    # PayloadID	PayloadTime	ContentType	URI	Attached To Type	Attached To	Title	Payload
    PYLD_ID = 0
    PYLD_TIME = 1
    PYLD_CONTENT_TYPE = 2
    PYLD_URI = 3
    PYLD_ATTACH_TYPE = 4
    PYLD_ATTACH = 5
    PYLD_TITLE = 6
    PYLD_PYLD = 7

    # take in various facility parameters
    def __init__(self, org_params, p_params):
        with open(self.PAYLOAD_HEADER_FILE) as header_file:
            self.PAYLOAD_HEADER = header_file.read()
            self.p_id = p_params[self.PYLD_ID]
            self.p_time = p_params[self.PYLD_TIME]
            self.p_content_type = p_params[self.PYLD_CONTENT_TYPE]
            self.p_uri = p_params[self.PYLD_URI]
            self.p_attach_type = p_params[self.PYLD_ATTACH_TYPE]
            self.p_attach = p_params[self.PYLD_ATTACH]
            self.p_title = p_params[self.PYLD_TITLE]
            self.p_pyld = p_params[self.PYLD_PYLD]
        return
    
    def __add_attribute(self, name, value):
        self.xml_string += '<' + name + '>' + str(value) + '</' + name + '>'
    '''
    <ift:payload xmlns:ift="urn:ibm:ift:xsd:1">
    <payloadMessage>
        <payloadID>spd1_vineyard_harvest1_payload1</payloadID>
        <payloadTime>2016-09-22T11:15:00Z</payloadTime>
        <payloadContentType>application/json</payloadContentType>
        <payloadTypeURI>urn:ibm:ift:payload:type:json:triple</payloadTypeURI>
        <eventIDList>
        <eventID>spd1_vineyard_harvest1</eventID>
        </eventIDList>
        <payload>[{"key":"title", "value":"Varietal Type","type":"string"}, {"key":"Varietals", "value":"Chardonnay","type":"string"}]</payload>
    </payloadMessage>
    </ift:payload>
    '''
    def __generate_xml(self):
        self.xml_string = self.PAYLOAD_HEADER
        self.xml_string += '<payloadMessage>'

        self.__add_attribute('payloadID', self.p_id)
        cc = CommonCoversions()
        self.__add_attribute('payloadTime', cc.time_in_iso_format(self.p_time))
        self.__add_attribute('payloadContentType', self.p_content_type)
        self.__add_attribute('payloadTypeURI', self.p_uri)

        # put in the attach info
        if self.p_attach_type == 'E':
            print(self.p_attach)
            utils.d_pprint(0, "Payload Attach", self.p_attach)
            self.xml_string += '<eventIDList>'
            x = self.p_attach.split(',')
            for event_id in x:
                self.__add_attribute('eventID', event_id)
            self.xml_string += '</eventIDList>'
        else:
            utils.quit("not yet implemented")

        self.xml_string += '<payload>'
        current_payload = json.loads(self.p_pyld)
        title_payload = {"key":"title", "value":self.p_title,"type":"string"}
        current_payload.append(title_payload)
        final_payload_str = json.dumps(current_payload)
        self.xml_string += final_payload_str
        self.xml_string += '</payload>'

        self.xml_string += self.PAYLOAD_FOOTER

        return self.xml_string

    def get_xml(self):
        return self.__generate_xml()