import requests
from dhis2_config import *

def get_org_unit_data(state_code):
    dhis2_org_unit_url = f"{dhis2_api_url}?filter=code:eq:{state_code}&fields=id,name,shortName,openingDate"
    response = requests.get(dhis2_org_unit_url, auth=(dhis2_username, dhis2_password))
    return response

def update_org_unit(org_unit_id, update_data):
    update_url = f"{dhis2_api_url}/{org_unit_id}"
    # response = requests.put(update_url, json=update_data, auth=(dhis2_username, dhis2_password))
    response = ""
    return response
