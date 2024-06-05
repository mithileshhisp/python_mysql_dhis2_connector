# dhis2_api_interaction.py
# Author: mithilesh
import requests
import json
import base64
from requests.auth import HTTPBasicAuth
from datetime import datetime
import logging

dhis2_api_url = "*******"
dhis2_username = "******"
dhis2_password = "******"
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

def get_org_unit_data(VanID):
    filters = [
        f"attributeValues.attribute.id:eq:OZW5netBBfD&level=3&paging=false",
        f"attributeValues.value:eq:{VanID}"
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
            error_message = f"No data received for PermSubDistrictId-- {VanID}"
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
    #print(f"org_unit_id {org_unit_id} " )
    #print(f"CreatedDate {enrollment_date} " )
    #print(f"enrollment_data {enrollment_data} " )

    responseJson = response.json()
    #print(f"enrollment_response 1 -- { responseJson }" )

    return response

def check_existing_tei(orgUnitID, beneficiary_mapping_reg_id):
    # for 104 program
    # tei_search_url = f"{enrollment_endpoint}?ouMode=ALL&program=vyQPQ07JB9M&filter=HKw3ToP2354:eq:{beneficiary_reg_id}"
    # for 1097 program
    #https://links.hispindia.org/amrit/api/trackedEntityInstances.json?ouMode=ALL&program=vyQPQ07JB9M&filter=HKw3ToP2354:eq:7393430
    #https://links.hispindia.org/amrit/api/trackedEntityInstances.json?ou=HExrvaAcDEB&ouMode=SELECTED&program=hQUeRtU70wj&filter=HKw3ToP2354:eq:7393430
    #https://samiksha.piramalswasthya.org/amrit/api/trackedEntityInstances.json?ou=cgc0mgUcaNG&ouMode=SELECTED&program=hQUeRtU70wj&filter=HKw3ToP2354:eq:290122
    tei_search_url = f"{enrollment_endpoint}?ou={orgUnitID}&ouMode=SELECTED&program=hQUeRtU70wj&filter=HKw3ToP2354:eq:{beneficiary_mapping_reg_id}"

    response = requests.get(tei_search_url, auth=HTTPBasicAuth(dhis2_username, dhis2_password))
    if response.status_code == 200:
        response_data = response.json()
        teis = response_data.get('trackedEntityInstances', [])
        return teis 
    else:
        return []
    

def get_tei_data(orgUnitID, BeneficiaryRegID, tei_data_cache):

    if BeneficiaryRegID in tei_data_cache:
        return tei_data_cache[BeneficiaryRegID]

    attribute_value = BeneficiaryRegID
    #"https://links.hispindia.org/amrit/api/trackedEntityInstances.json?ouMode=ALL&program=hQUeRtU70wj&fields=trackedEntityInstance,orgUnit,enrollments[program,enrollment,orgUnitName]&filter=HKw3ToP2354:EQ:5773626"
    #https://links.hispindia.org/amrit/api/trackedEntityInstances.json?ouMode=ALL&program=hQUeRtU70wj&fields=trackedEntityInstance,orgUnit,enrollments[program,enrollment,orgUnitName]&filter=HKw3ToP2354:EQ:1
    #url = f"{dhis2_base_url}trackedEntityInstances.json?ouMode=ALL&program=vyQPQ07JB9M&fields=trackedEntityInstance,orgUnit&filter=HKw3ToP2354:EQ:{attribute_value}"
    
    tei_search_url = f"{enrollment_endpoint}?ou={orgUnitID}&ouMode=SELECTED&program=hQUeRtU70wj&filter=HKw3ToP2354:eq:{attribute_value}"

    #print( tei_search_url )
    response = requests.get(tei_search_url, auth=(dhis2_username, dhis2_password))

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


def construct_event_payload(tei_data, CreatedDate, BenVisitID, BeneficiaryRegID, VisitNo, AgeOnVisit, 
                            VisitReason, VisitCategory, RCHID, ProvisionalDiagnosis, 
                            SystolicBP_1stReading, DiastolicBP_1stReading, Status, 
                            referredToInstituteName, ProcedureName, NCD_Condition1, NCD_Condition2, 
                            NCD_Condition3, NCD_Condition4, DiagnosisProvided1, DiagnosisProvided2, 
                            DiagnosisProvided3, DiagnosisProvided4, DiagnosisProvided5):
    

    orgUnit = tei_data["orgUnit"]
    tei_uid = tei_data["trackedEntityInstance"]

    event_payload = {
        "program": "hQUeRtU70wj",
        "orgUnit": orgUnit,
        "eventDate": CreatedDate,
        "programStage": "gpZJwMDObuC",
        "status": "ACTIVE",
        "trackedEntityInstance": tei_uid,
        "dataValues": [
            {"dataElement": "Q7aA5HvvV7L", "value": assign_value_if_not_null(BenVisitID)},
            {"dataElement": "hzYStHHLxQy", "value": assign_value_if_not_null(VisitNo)},
            {"dataElement": "P5a5E6m8llj", "value": assign_value_if_not_null(AgeOnVisit)},
            {"dataElement": "GwHcyOdg4CD", "value": remove_space_if_not_null(VisitReason)},
            {"dataElement": "oTsj7lfUVgo", "value": remove_space_if_not_null(VisitCategory)},
            {"dataElement": "LyKVDsTWOVv", "value": assign_value_if_not_null(RCHID)},
            {"dataElement": "wBL3WAU2bTC", "value": remove_space_if_not_null(ProvisionalDiagnosis)},
            {"dataElement": "X8UNYvbZ9wV", "value": assign_value_if_not_null(SystolicBP_1stReading)},
            {"dataElement": "wwy7WCpuqfv", "value": assign_value_if_not_null(DiastolicBP_1stReading)},
            {"dataElement": "N8i9krC5HpK", "value": remove_space_if_not_null(Status)},
            {"dataElement": "KtoABiKQ6lK", "value": remove_space_if_not_null(referredToInstituteName)},
            {"dataElement": "R8AEzCJEcE5", "value": remove_space_if_not_null(ProcedureName)},
            {"dataElement": "fa4AJy44Uhx", "value": remove_space_if_not_null(NCD_Condition1)},
            {"dataElement": "SamGFJEYgDT", "value": remove_space_if_not_null(NCD_Condition2)},
            {"dataElement": "iqO4o5uiXHU", "value": remove_space_if_not_null(NCD_Condition3)},
            {"dataElement": "DupwTvIo75R", "value": remove_space_if_not_null(NCD_Condition4)},
            {"dataElement": "d5Nyb78pT99", "value": remove_space_if_not_null(DiagnosisProvided1)},
            {"dataElement": "vgEe9iXxTLa", "value": remove_space_if_not_null(DiagnosisProvided2)},
            {"dataElement": "abc6hYLxX63", "value": remove_space_if_not_null(DiagnosisProvided3)},
            {"dataElement": "oizsMuSKKHu", "value": remove_space_if_not_null(DiagnosisProvided4)},
            {"dataElement": "mohldt3jMiZ", "value": remove_space_if_not_null(DiagnosisProvided5)}

        ]
    }
    #print(f"event_payload: {event_payload}" )

    return event_payload

def assign_value_if_not_null(value):
    if value is not None and value != "null":
        return value
    else:
        return ""

def remove_space_if_not_null(value):
    if value is not None and value != "null":
        return value.strip()
    else:
        return ""


def create_events_in_dhis2(multiple_events_payload,BeneficiaryRegID, BenVisitID):
    #print(f"multiple_events_payload : {multiple_events_payload}")
    response = requests.post(
        f"{dhis2_api_url}events",
        json=multiple_events_payload,
        auth=(dhis2_username, dhis2_password)
    )

    if response.status_code == 200:
        event_uid = response.json().get("response", {}).get("importSummaries", [])[0].get("reference")
        #event_ids = [item.get("event") for item in response.json().get("response", {}).get("importSummaries", [])[0].get("importCount",{}).get("imported")]
        #print(f"Events created successfully. Event IDs: {response.json()}")
        event_count = response.json().get("response", {}).get("importSummaries", [])[0].get("importCount",{}).get("imported")
        print(f"Events created successfully. BenVisitID : {BenVisitID} . BeneficiaryRegID : {BeneficiaryRegID}. Event count: {event_count} . imported event : {event_uid}")
        logging.info(f"Events created successfully. BenVisitID : {BenVisitID} . BeneficiaryRegID : {BeneficiaryRegID}. Event count: {event_count}. imported event : {event_uid}")
        #logging.info(f"Event created successfully . BenVisitID : {BenVisitID} . BeneficiaryRegID : {BeneficiaryRegID}. Event count: {event_count}. Event uid: {event_uid}" )
        #logging.info("MySQL connection closed")

    else:
        print(f"Failed to create events. Error: {response.text}")
        logging.error(f"Failed to create events . BenVisitID : {BenVisitID} . BeneficiaryRegID : {BeneficiaryRegID}. Status code: {response.status_code} . error details: {response.json()} .Error: {response.text}")

