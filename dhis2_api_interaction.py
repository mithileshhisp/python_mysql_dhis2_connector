# dhis2_api_interaction.py
# Author: mithilesh
import requests
import json
import base64
from requests.auth import HTTPBasicAuth
from datetime import datetime
import logging

dhis2_api_url = ""
dhis2_username = ""
dhis2_password = ""
org_unit_api_url = f"{dhis2_api_url}organisationUnits"
options_api_url = f"{dhis2_api_url}options"
enrollment_endpoint = f"{dhis2_api_url}trackedEntityInstances"

def get_org_unit_and_option_data(PermSubDistrictId, PermVillageId):
    filters = [
        f"attributeValues.attribute.id:eq:l38VgCtdLFD",
        f"attributeValues.value:eq:{PermSubDistrictId}",
        "level:eq:4"
    ]

    url_with_filters = f"{org_unit_api_url}?fields=id,name,level,attributeValues&filter={'&filter='.join(filters)}"

    filters1 = [
        f"attributeValues.attribute.id:eq:RDZKbFFn7EL",
        f"attributeValues.value:eq:{PermVillageId}"
    ]

    url_with_filters1 = f"{options_api_url}?fields=id,displayName,attributeValues&filter={'&filter='.join(filters1)}"

    response_org_unit = requests.get(url_with_filters, auth=HTTPBasicAuth(dhis2_username, dhis2_password))
    response_options = requests.get(url_with_filters1, auth=HTTPBasicAuth(dhis2_username, dhis2_password))

    if response_org_unit.status_code == 200 and response_options.status_code == 200:
        response_data_org_unit = response_org_unit.json()
        response_data_options = response_options.json()

        org_unit_data = response_data_org_unit.get('organisationUnits', [])
        option_data = response_data_options.get('options', [])

        if org_unit_data:
            for org_unit in org_unit_data:
                org_unit_id = org_unit['id']
                org_unit_name = org_unit['name']
        else:
            error_message = f"No data received for PermSubDistrictId-- {PermSubDistrictId}"
            print(error_message)

        if option_data:
            option_id = option_data[0]['id']
            option_name = option_data[0]['displayName']
        else:
            error_message = f"No option data PermVillageId-- {PermVillageId}."
            print(error_message)
    else:
        print(f"Failed to retrieve organization units. Status code: {response_org_unit.status_code}")
        print(f"Failed to retrieve options. Status code: {response_options.status_code}")

    return org_unit_id, option_name

def get_org_unit_data(PermDistrictId):
    filters = [
        f"attributeValues.attribute.id:eq:l38VgCtdLFD&level=3&paging=false",
        f"attributeValues.value:eq:{PermDistrictId}"
    ]

    url_with_filters = f"{org_unit_api_url}?fields=id,name,level,attributeValues&filter={'&filter='.join(filters)}"

    #print(f"url_with_filters : {url_with_filters}")

    response_org_unit = requests.get(url_with_filters, auth=HTTPBasicAuth(dhis2_username, dhis2_password))


    if response_org_unit.status_code == 200:
        response_data_org_unit = response_org_unit.json()
        
        org_unit_data = response_data_org_unit.get('organisationUnits', [])
        
        if org_unit_data:
            for org_unit in org_unit_data:
                org_unit_id = org_unit['id']
                org_unit_name = org_unit['name']
        else:
            error_message = f"No data received for PermSubDistrictId-- {PermDistrictId}"
            print(error_message)

    else:
        print(f"Failed to retrieve organization units. Status code: {response_org_unit.status_code}")

    return org_unit_id


def create_enrollment(enrollment_data, org_unit_id,enrollment_date):
    #CreatedDate = enrollment_data["attributes"][3]["value"]
    #CreatedDate = datetime.strptime(enrollment_date, "%Y-%m-%d").strftime("%Y-%m-%d")

    #enrollment_data["orgUnit"] = org_unit_id
    enrollment_data["enrollments"][0]["orgUnit"] = org_unit_id
    enrollment_data["enrollments"][0]["enrollmentDate"] = enrollment_date
    enrollment_data["enrollments"][0]["incidentDate"] = enrollment_date

    response = requests.post(
        enrollment_endpoint,
        data=json.dumps(enrollment_data),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Basic {base64.b64encode(f'{dhis2_username}:{dhis2_password}'.encode()).decode()}"
        }
    )
    print(f"org_unit_id {org_unit_id} " )
    print(f"CreatedDate {enrollment_date} " )
    #print(f"enrollment_data {enrollment_data} " )

    responseJson = response.json()
    print(f"enrollment_response 1 -- { responseJson }" )

    return response

def check_existing_tei(beneficiary_mapping_reg_id):
    # for 104 program
    # tei_search_url = f"{enrollment_endpoint}?ouMode=ALL&program=vyQPQ07JB9M&filter=HKw3ToP2354:eq:{beneficiary_reg_id}"
    # for 1097 program
    #https://links.hispindia.org/amrit/api/trackedEntityInstances.json?ouMode=ALL&program=vyQPQ07JB9M&filter=HKw3ToP2354:eq:7393430
    tei_search_url = f"{enrollment_endpoint}?ouMode=ALL&program=vyQPQ07JB9M&filter=HKw3ToP2354:eq:{beneficiary_mapping_reg_id}"

    response = requests.get(tei_search_url, auth=HTTPBasicAuth(dhis2_username, dhis2_password))
    if response.status_code == 200:
        response_data = response.json()
        teis = response_data.get('trackedEntityInstances', [])
        return teis 
    else:
        return []
    

def get_tei_data(dhis2_base_url, dhis2_username, dhis2_password, BeneficiaryRegID, tei_data_cache):

    if BeneficiaryRegID in tei_data_cache:
        return tei_data_cache[BeneficiaryRegID]

    attribute_value = BeneficiaryRegID
    #"https://links.hispindia.org/amrit/api/trackedEntityInstances.json?ouMode=ALL&program=hQUeRtU70wj&fields=trackedEntityInstance,orgUnit,enrollments[program,enrollment,orgUnitName]&filter=HKw3ToP2354:EQ:5773626"
    #https://links.hispindia.org/amrit/api/trackedEntityInstances.json?ouMode=ALL&program=hQUeRtU70wj&fields=trackedEntityInstance,orgUnit,enrollments[program,enrollment,orgUnitName]&filter=HKw3ToP2354:EQ:1
    url = f"{dhis2_base_url}trackedEntityInstances.json?ouMode=ALL&program=vyQPQ07JB9M&fields=trackedEntityInstance,orgUnit&filter=HKw3ToP2354:EQ:{attribute_value}"
    #print( url )
    response = requests.get(url, auth=(dhis2_username, dhis2_password))

    if response.status_code == 200:
        tei_data = response.json()
        if tei_data.get("trackedEntityInstances"):
            tei_data = tei_data["trackedEntityInstances"][0]
            tei_data_cache[BeneficiaryRegID] = tei_data
            return tei_data
        else:
            print(f"TEI data not found for BeneficiaryRegID: {BeneficiaryRegID}" )
            #print(f"TEI data not found for BeneficiaryRegID: {BeneficiaryRegID}" )
            logging.info(f"TEI data not found for BeneficiaryRegID {BeneficiaryRegID}" )
            return None
    else:
        print(f"Failed to fetch TEI data for BeneficiaryRegID: {BeneficiaryRegID}")
        logging.info(f"Failed to fetch TEI data for BeneficiaryRegID {BeneficiaryRegID} error details: {response.json()}" )
        print(f"response: {response}" )
        return None


def construct_event_payload(tei_data, CreatedDate, BenCallID, CallID, AgeOnVisit, IsOutbound, 
                            CategoryName, SubCategoryName, PrescriptionID, ReceivedRoleName,
                            CallDurationInSeconds, CallType, CallGroupType, Diasease, data_dict ):
    

    orgUnit = tei_data["orgUnit"]
    tei_uid = tei_data["trackedEntityInstance"]

    #key_to_check = Diasease

    temp_Diasease = ''
    if Diasease is not None and Diasease != "null":

        if data_dict.get(Diasease) is not None:
            #print(f"Key '{key_to_check}' exists.")
            temp_Diasease = data_dict.get(Diasease)
        else:
            #print(f"Key '{Diasease}' does not exist.")
            temp_Diasease = ''
            
        event_payload = {
        "program": "vyQPQ07JB9M",
        "orgUnit": orgUnit,
        "eventDate": CreatedDate,
        "programStage": "ISSSjurI0kD",
        "status": "ACTIVE",
        "trackedEntityInstance": tei_uid,
        "dataValues": [
            {"dataElement": "hsbXpo83f4I", "value": assign_value_if_not_null(BenCallID)},
            {"dataElement": "dVQRpxXgMEd", "value": assign_value_if_not_null(CallID)},
            {"dataElement": "P5a5E6m8llj", "value": assign_value_if_not_null(AgeOnVisit)},
            {"dataElement": "IZ8umfwfXSm", "value": assign_value_if_not_null(IsOutbound)},
            {"dataElement": "sSWrwFFrd94", "value": assign_value_if_not_null(CategoryName)},
            {"dataElement": "C5CFVWUYfeQ", "value": assign_value_if_not_null(SubCategoryName)},
            {"dataElement": "CBZkvkRRnOl", "value": assign_value_if_not_null(PrescriptionID)},
            {"dataElement": "hUDunUrmF14", "value": assign_value_if_not_null(ReceivedRoleName)},
            {"dataElement": "ZTNtr3RK0kh", "value": assign_value_if_not_null(CallDurationInSeconds)},
            {"dataElement": "ioNKjuWD3s9", "value": assign_value_if_not_null(CallType)},
            {"dataElement": "CBZkvkRRnOl", "value": assign_value_if_not_null(PrescriptionID)},
            {"dataElement": "UUKDfFwHMfA", "value": assign_value_if_not_null(CallGroupType)},
            {"dataElement": "CJXPDQOnSy7", "value": temp_Diasease}
        ]
    }
        #print(f"event_payload: {event_payload}" )
    else:
        event_payload = {
        "program": "vyQPQ07JB9M",
        "orgUnit": orgUnit,
        "eventDate": CreatedDate,
        "programStage": "ISSSjurI0kD",
        "status": "ACTIVE",
        "trackedEntityInstance": tei_uid,
        "dataValues": [
            {"dataElement": "hsbXpo83f4I", "value": assign_value_if_not_null(BenCallID)},
            {"dataElement": "dVQRpxXgMEd", "value": assign_value_if_not_null(CallID)},
            {"dataElement": "P5a5E6m8llj", "value": assign_value_if_not_null(AgeOnVisit)},
            {"dataElement": "IZ8umfwfXSm", "value": assign_value_if_not_null(IsOutbound)},
            {"dataElement": "sSWrwFFrd94", "value": assign_value_if_not_null(CategoryName)},
            {"dataElement": "C5CFVWUYfeQ", "value": assign_value_if_not_null(SubCategoryName)},
            {"dataElement": "CBZkvkRRnOl", "value": assign_value_if_not_null(PrescriptionID)},
            {"dataElement": "hUDunUrmF14", "value": assign_value_if_not_null(ReceivedRoleName)},
            {"dataElement": "ZTNtr3RK0kh", "value": assign_value_if_not_null(CallDurationInSeconds)},
            {"dataElement": "ioNKjuWD3s9", "value": assign_value_if_not_null(CallType)},
            {"dataElement": "CBZkvkRRnOl", "value": assign_value_if_not_null(PrescriptionID)},
            {"dataElement": "UUKDfFwHMfA", "value": assign_value_if_not_null(CallGroupType)}
        ]
    }
    #print(f"event_payload: {event_payload}" )

    return event_payload

def assign_value_if_not_null(value):
    if value is not None and value != "null":
        return value
    else:
        return ""

def create_events_in_dhis2(dhis2_base_url, dhis2_username, dhis2_password, multiple_events_payload,BeneficiaryRegID, BenCallID):
    #print(f"multiple_events_payload : {multiple_events_payload}")
    response = requests.post(
        f"{dhis2_base_url}events",
        json=multiple_events_payload,
        auth=(dhis2_username, dhis2_password)
    )

    if response.status_code == 200:
        event_uid = response.json().get("response", {}).get("importSummaries", [])[0].get("reference")
        #event_ids = [item.get("event") for item in response.json().get("response", {}).get("importSummaries", [])[0].get("importCount",{}).get("imported")]
        #print(f"Events created successfully. Event IDs: {response.json()}")
        event_count = response.json().get("response", {}).get("importSummaries", [])[0].get("importCount",{}).get("imported")
        print(f"Events created successfully. BenCallID : {BenCallID} . BeneficiaryRegID : {BeneficiaryRegID}. Event count: {event_count} . imported event : {event_uid}")
        logging.info(f"Events created successfully. BenCallID : {BenCallID} . BeneficiaryRegID : {BeneficiaryRegID}. Event count: {event_count}. imported event : {event_uid}")
        #logging.info(f"Event created successfully . BenVisitID : {BenVisitID} . BeneficiaryRegID : {BeneficiaryRegID}. Event count: {event_count}. Event uid: {event_uid}" )
        #logging.info("MySQL connection closed")

    else:
        print(f"Failed to create events. Error: {response.text}")
        logging.error(f"Failed to create events . BenCallID : {BenCallID} . BeneficiaryRegID : {BeneficiaryRegID}. Status code: {response.status_code} . error details: {response.json()}")

