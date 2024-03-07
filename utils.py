# utils.py
import requests
import logging
from constants import DHIS2_API_URL, DHIS2_AUTH, LOG_FILE

def configure_logging():
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def log_info(message):
    logging.info(message)

def log_error(message):
    logging.error(message)
'''
def get_dhis2_orgunit_level4():
#orgUnitsAttributeValue = {}
    params = {
        "filter": "level:eq:4",
        "fields": "id,displayName,shortName,code,level,attributeValues[attribute[id,displayName,code],value]&paging=false&filter=level:eq:4",
    }
    response = requests.get(f"{DHIS2_API_URL}/organisationUnits?fields=id,displayName,shortName,code,level,attributeValues[attribute[id,displayName,code],value]&sortOrder=ASC&paging=false&filter=level:eq:4", auth=DHIS2_AUTH)
    if response.status_code == 200:
        orgUnitsAttributeValue = {}
        orgunits = response.json()["organisationUnits"]
        #print( response.status_code )
        print( len(orgunits ) )
        for orgunit in orgunits:
            #print( orgunit )
            attrValues = orgunit["attributeValues"]
            #print( attrValues )
            for attrValue in attrValues:
                if attrValue["attribute"]["code"] == "amritFacilityPrimaryKey":
                    #print( attrValue["attribute"]["code"] )
                    #print( attrValue["value"] )
                    #print( orgunit["id"] )
                    orgUnitsAttributeValue[attrValue["value"]] = orgunit["id"]

                        #return orgUnitsAttributeValue

    return orgUnitsAttributeValue

    '''