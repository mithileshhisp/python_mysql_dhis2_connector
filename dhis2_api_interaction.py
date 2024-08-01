# dhis2_api_interaction.py
# Author: mithilesh
import requests
import json
import base64
from requests.auth import HTTPBasicAuth
from datetime import datetime
import logging
import pandas as pd

dhis2_api_url = "####"
dhis2_username = "####"
dhis2_password = "####"
org_unit_api_url = f"{dhis2_api_url}organisationUnits"
options_api_url = f"{dhis2_api_url}options"
enrollment_endpoint = f"{dhis2_api_url}trackedEntityInstances"
event_endpoint = f"{dhis2_api_url}events.json"

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
        f"attributeValues.attribute.id:eq:dxsfy49ePQY&level=3&paging=false",
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
    #https://links.hispindia.org/amrit/api/trackedEntityInstances.json?ou=HExrvaAcDEB&ouMode=SELECTED&program=vyQPQ07JB9M&filter=HKw3ToP2354:eq:7393430
    #https://samiksha.piramalswasthya.org/amrit/api/trackedEntityInstances.json?ou=cgc0mgUcaNG&ouMode=SELECTED&program=NMGbY2nXCKu&filter=HKw3ToP2354:eq:290122
    tei_search_url = f"{enrollment_endpoint}?ou={orgUnitID}&ouMode=SELECTED&program=NMGbY2nXCKu&filter=HKw3ToP2354:eq:{beneficiary_mapping_reg_id}"

    #print(tei_search_url)
    #print(f" tei_search_url : {tei_search_url}" )
    response = requests.get(tei_search_url, auth=HTTPBasicAuth(dhis2_username, dhis2_password))
    if response.status_code == 200:
        response_data = response.json()
        teis = response_data.get('trackedEntityInstances', [])
        return teis 
    else:
        return []
    

def get_tei_data(org_unit_id, BeneficiaryRegID, tei_data_cache):

    if BeneficiaryRegID in tei_data_cache:
        return tei_data_cache[BeneficiaryRegID]

    attribute_value = BeneficiaryRegID
    #"https://links.hispindia.org/amrit/api/trackedEntityInstances.json?ouMode=ALL&program=hQUeRtU70wj&fields=trackedEntityInstance,orgUnit,enrollments[program,enrollment,orgUnitName]&filter=HKw3ToP2354:EQ:5773626"
    #https://links.hispindia.org/amrit/api/trackedEntityInstances.json?ouMode=ALL&program=hQUeRtU70wj&fields=trackedEntityInstance,orgUnit,enrollments[program,enrollment,orgUnitName]&filter=HKw3ToP2354:EQ:1
    #url = f"{dhis2_api_url}trackedEntityInstances.json?ouMode=ALL&program=NMGbY2nXCKu&fields=trackedEntityInstance,orgUnit&filter=HKw3ToP2354:EQ:{attribute_value}"
    url = f"{dhis2_api_url}trackedEntityInstances.json?ou={org_unit_id}&ouMode=SELECTED&program=NMGbY2nXCKu&fields=trackedEntityInstance,orgUnit&filter=HKw3ToP2354:EQ:{attribute_value}"
    #tei_search_url = f"{enrollment_endpoint}?ou={orgUnitID}&ouMode=SELECTED&program=NMGbY2nXCKu&filter=HKw3ToP2354:eq:{beneficiary_mapping_reg_id}"

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

def check_existing_event(orgUnitID, ven_visit_code):
    
    #JH MMU check event exist with dataelement value
    #https://samiksha.piramalswasthya.org/amrit/api/events.json?orgUnit=iLxzohR8kRW&ouMode=SELECTED&program=NMGbY2nXCKu&status=ACTIVE&skipPaging=true&filter=QRE1IBSOKdE:eq:30003100010467
    #https://samiksha.piramalswasthya.org/amrit/api/events.json?program=NMGbY2nXCKu&orgUnit=iLxzohR8kRW&ouMode=SELECTED&status=ACTIVE&filter=QRE1IBSOKdE:eq:30003100010467&skipPaging=true
    event_search_url = f"{event_endpoint}?orgUnit={orgUnitID}&ouMode=SELECTED&program=NMGbY2nXCKu&status=ACTIVE&skipPaging=true&filter=QRE1IBSOKdE:eq:{ven_visit_code}"

    #print(event_search_url)
    #print(f" event_search_url : {event_search_url}" )
    response = requests.get(event_search_url, auth=HTTPBasicAuth(dhis2_username, dhis2_password))
    if response.status_code == 200:
        response_data = response.json()
        events = response_data.get('events', [])
        return events 
    else:
        return []



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
        "program": "NMGbY2nXCKu",
        "orgUnit": orgUnit,
        "eventDate": CreatedDate,
        "programStage": "qJbHjQBuG3G",
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
        "program": "NMGbY2nXCKu",
        "orgUnit": orgUnit,
        "eventDate": CreatedDate,
        "programStage": "qJbHjQBuG3G",
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

def construct_sql_query_event_payload(tei_data, Visitcode, BenVisitID, BeneficiaryRegID,
                       VisitNo, CreatedDate, vanid, AgeOnVisit, VisitReason, VisitCategory, PregnancyStatus,
                       Referal_Visitcode, referredToInstituteName, referralreason,ProvisionalDiagnosis,
                       phyanthropometry_bmi, nurse_rbs, Weight_Kg, Height_cm, WaistCircumference_cm,
                       Temperature, SystolicBP_1stReading, DiastolicBP_1stReading, ComorbidCondition_Fulltext,
                       Comobrid_Diabetes,Comobrid_Hypertension,Comobrid_Asthma,Comobrid_Epilepsy,Comobrid_Heart_Disease,
                       Comobrid_Kidney_Disease,Comobrid_Sickle_cell,Labtest_Prescribed, Drug_Prescribedcode, Drug_Dispensecode,
                       diagnosisprovided_full_text, DiagnosisProvided1, NCD_Condition, ncd_condition_full_text,
                       PulseRate, spo2, feto_Visitcode,TestName, GenericDrugName, Labtest_Done_Visitcode,Total_lab_test,
                       Random_Blood_Sugar, Hemoglobin, UrineAlbumin, UrineSugar, Urine_Pregnancy_test, Malaria, ECG, HbA1c,
                       Liver_Function_Test, Liverfunctiontest_Direct_Bilirubin, Liverfunctiontest_SGPT, Liverfunctiontest_SGOT,
                       Liverfunctiontest_Total_Serum_Bilirubin, Liverfunctiontest_Blood_Urea, Liverfunctiontest_Serum_Creatinine,
                       Renal_function_test, Renalfunctiontest_Serum_Creatinine, Renalfunctiontest_Blood_Urea,
                       Lipid_profile, Lipidprofile_Serum_Total_Cholesterol, Lipidprofile_Serum_HDL, Lipidprofile_LDL, Lipidprofile_Serum_Triglycerides,
                       Post_Lunch_Blood_Sugar, Fasting_Blood_Sugar, Complete_Blood_Picture, CBP_ESR, CBP_Monocytes,
                       CBP_Hemoglobin, CBP_RBC, CBP_Lymphocytes, CBP_Neutrophils, CBP_Basophils, CBP_Eosinophils, CBP_MCV,
                       CBP_MCH, CBP_MCHC, CBP_Hematocrit, CBP_Platelet_Count, CBP_Total_Leucocyte_Count, Widal_Test,
                       Sputum_AFB_Test, Sickle_Cell_Disease_Test, HBsAg, Complete_Urine_Examination,
                       Complete_Urine_Examination_Total_Leucocyte_Count, Complete_Urine_Examination_Urine_for_Nitrite,
                       Chikungunya, Hb_Electrophoresis, Dengue_NS1_Antigen, Dengue_Antibody_Test,
                       HIV1_HIV2_RDT, Visual_Acuity_Test, Blood_Group, VDRL_Test, Syphilis, Serum_Uric_Acid, Serum_Total_Cholesterol,
                       Hepatitis_B, Hepatitis_C, ESR, RBS_Status ):
    
    orgUnit = tei_data["orgUnit"]
    tei_uid = tei_data["trackedEntityInstance"]
    eventDate = CreatedDate.strftime("%Y-%m-%d")

    existing_event = check_existing_event(orgUnit, Visitcode)

    #print(f"event_payload: {existing_event[0]['orgUnitName']}" )
    if existing_event:
        print(f"Event already exists for Visitcode {Visitcode}. BeneficiaryRegID {BeneficiaryRegID}. orgUnit Id {orgUnit} . orgUnitName {existing_event[0]['orgUnitName']}. Skipping.")
        logging.info(f"Event already exists for Visitcode {Visitcode} . BeneficiaryRegID {BeneficiaryRegID}. orgUnit Id {orgUnit} . orgUnitName {existing_event[0]['orgUnitName']}. Skipping.")
        return

    event_payload = {
        #"event" : event,
        "program": "NMGbY2nXCKu",
        "orgUnit": orgUnit,
        "eventDate": eventDate,
        "programStage": "qJbHjQBuG3G",
        "status": "ACTIVE",
        "trackedEntityInstance": tei_uid,
        "dataValues": [
            {"dataElement": "QRE1IBSOKdE", "value": assign_value_if_NaN(Visitcode)},
            {"dataElement": "Q7aA5HvvV7L", "value": assign_value_if_NaN(BenVisitID)},
            {"dataElement": "hzYStHHLxQy", "value": assign_value_if_NaN(VisitNo)},
            {"dataElement": "P5a5E6m8llj", "value": assign_value_if_NaN(AgeOnVisit)},
            {"dataElement": "GwHcyOdg4CD", "value": assign_value_if_NaN(VisitReason)},
            {"dataElement": "oTsj7lfUVgo", "value": assign_value_if_NaN(VisitCategory)},
            {"dataElement": "s3afEOkQTlg", "value": assign_value_if_NaN(PregnancyStatus)},
            {"dataElement": "AKMkMnWNiG1", "value": assign_value_if_NaN(Referal_Visitcode)},
            {"dataElement": "KtoABiKQ6lK", "value": assign_value_if_NaN(referredToInstituteName)},
            {"dataElement": "ryiIUM1S8ar", "value": assign_value_if_NaN(referralreason)},
            {"dataElement": "wBL3WAU2bTC", "value": assign_value_if_NaN(ProvisionalDiagnosis)},
            {"dataElement": "pohCVodbTm6", "value": assign_value_if_NaN(phyanthropometry_bmi)},
            {"dataElement": "s7vpadfqfmS", "value": assign_value_if_NaN(nurse_rbs)},
            {"dataElement": "vRc7DmJMEQI", "value": assign_value_if_NaN(Weight_Kg)},  
            {"dataElement": "vw8R2gyAuPo", "value": assign_value_if_NaN(Height_cm)},     
            {"dataElement": "QV2NY50zE1E", "value": assign_value_if_NaN(WaistCircumference_cm)},    
            {"dataElement": "prXoT8ZJdiv", "value": assign_value_if_NaN(Temperature)}, 
            {"dataElement": "X8UNYvbZ9wV", "value": assign_value_if_NaN(SystolicBP_1stReading)},
            {"dataElement": "wwy7WCpuqfv", "value": assign_value_if_NaN(DiastolicBP_1stReading)},
            {"dataElement": "rgcw6SjzDYn", "value": assign_value_if_NaN(ComorbidCondition_Fulltext)},
            {"dataElement": "TttgfrMMSby", "value": assign_value_if_NaN(Comobrid_Diabetes)},
            {"dataElement": "LmmrcssSi8F", "value": assign_value_if_NaN(Comobrid_Hypertension)},
            {"dataElement": "xd4Qt4AM213", "value": assign_value_if_NaN(Comobrid_Asthma)},
            {"dataElement": "WfnpRqRWEHM", "value": assign_value_if_NaN(Comobrid_Epilepsy)},
            {"dataElement": "SuSHF1kefrG", "value": assign_value_if_NaN(Comobrid_Heart_Disease)},
            {"dataElement": "tgQbzqXDNRP", "value": assign_value_if_NaN(Comobrid_Kidney_Disease)},
            {"dataElement": "FyhwhFUY0nh", "value": assign_value_if_NaN(Comobrid_Sickle_cell)},
            {"dataElement": "SEWpIBXOVJr", "value": assign_value_if_NaN(Labtest_Prescribed)},
            {"dataElement": "pgdoeXKo0GL", "value": assign_value_if_NaN(Drug_Prescribedcode)},
            {"dataElement": "wH98g3BPtD1", "value": assign_value_if_NaN(Drug_Dispensecode)},
            {"dataElement": "XppQ0DsgMEF", "value": assign_value_if_NaN(diagnosisprovided_full_text)},
            {"dataElement": "d5Nyb78pT99", "value": assign_value_if_NaN(DiagnosisProvided1)} ,        
            {"dataElement": "fa4AJy44Uhx", "value": assign_value_if_NaN(NCD_Condition)},
            {"dataElement": "NcOvQWsZFuU", "value": assign_value_if_NaN(ncd_condition_full_text)},
            {"dataElement": "zgCKfBhHMap", "value": assign_value_if_NaN(PulseRate)},
            {"dataElement": "kT0JD27zJmU", "value": assign_value_if_NaN(spo2)},
            {"dataElement": "t61yi6jTQpa", "value": assign_value_if_NaN(feto_Visitcode)},
            {"dataElement": "fgo6djgo0Nn", "value": assign_value_if_NaN(TestName)},
            {"dataElement": "nBSZtCvhfFi", "value": assign_value_if_NaN(GenericDrugName)},
            {"dataElement": "E3ObN0pnxhJ", "value": assign_value_if_NaN(Labtest_Done_Visitcode)},
            {"dataElement": "lWvLH2vpEGU", "value": assign_value_if_NaN(Total_lab_test)},
            {"dataElement": "erQc3s2U1RN", "value": assign_value_if_NaN(Random_Blood_Sugar)},
            {"dataElement": "P73ZGr9cIWh", "value": assign_value_if_NaN(Hemoglobin)},
            {"dataElement": "WwbiEklafqD", "value": assign_value_if_NaN(UrineAlbumin)},
            {"dataElement": "C8haFJv6IYE", "value": assign_value_if_NaN(UrineSugar)},
            {"dataElement": "bxAncSyrRwq", "value": assign_value_if_NaN(Urine_Pregnancy_test)},
            {"dataElement": "O3zLLcKw6Zs", "value": assign_value_if_NaN(Malaria)},
            {"dataElement": "ppIBftFjyvg", "value": assign_value_if_NaN(ECG)},
            {"dataElement": "VXJSZCJECMl", "value": assign_value_if_NaN(HbA1c)},
            {"dataElement": "wQXTxsIcrUh", "value": assign_value_if_NaN(Liver_Function_Test)},
            {"dataElement": "KUbWxjd1Pn2", "value": assign_value_if_NaN(Liverfunctiontest_Direct_Bilirubin)},
            {"dataElement": "zrcWf9wrb7Q", "value": assign_value_if_NaN(Liverfunctiontest_SGPT)},
            {"dataElement": "QssPLOEFFLv", "value": assign_value_if_NaN(Liverfunctiontest_SGOT)},
            {"dataElement": "YUT6t2rf4As", "value": assign_value_if_NaN(Liverfunctiontest_Total_Serum_Bilirubin)},
            {"dataElement": "N6QoKvXeYE9", "value": assign_value_if_NaN(Liverfunctiontest_Blood_Urea)},
            {"dataElement": "k7Jcp85dGeU", "value": assign_value_if_NaN(Liverfunctiontest_Serum_Creatinine)},
            {"dataElement": "Qc5M9bwj9be", "value": assign_value_if_NaN(Renal_function_test)},
            {"dataElement": "PgIxHAG8tKJ", "value": assign_value_if_NaN(Renalfunctiontest_Serum_Creatinine)},
            {"dataElement": "N386Wicr2BF", "value": assign_value_if_NaN(Renalfunctiontest_Blood_Urea)},
            {"dataElement": "f4RwwhAYsPG", "value": assign_value_if_NaN(Lipid_profile)},
            {"dataElement": "BouZJY2f9ci", "value": assign_value_if_NaN(Lipidprofile_Serum_Total_Cholesterol)},
            {"dataElement": "U9HmdhXbmOE", "value": assign_value_if_NaN(Lipidprofile_Serum_HDL)},
            {"dataElement": "zFpoX3vUfYz", "value": assign_value_if_NaN(Lipidprofile_LDL)},
            {"dataElement": "lfybIrKEtug", "value": assign_value_if_NaN(Lipidprofile_Serum_Triglycerides)},
            {"dataElement": "XigK2YJCJeA", "value": assign_value_if_NaN(Post_Lunch_Blood_Sugar)},
            {"dataElement": "oTTHBvI4lCR", "value": assign_value_if_NaN(Fasting_Blood_Sugar)},
            {"dataElement": "oulQE5uBdPE", "value": assign_value_if_NaN(Complete_Blood_Picture)},
            {"dataElement": "GuWsng25Ejm", "value": assign_value_if_NaN(CBP_ESR)},
            {"dataElement": "EpDktJlqflN", "value": assign_value_if_NaN(CBP_Monocytes)},
            {"dataElement": "jb41MTR49ud", "value": assign_value_if_NaN(CBP_Hemoglobin)},
            {"dataElement": "usmFpkYjuFV", "value": assign_value_if_NaN(CBP_RBC)},
            {"dataElement": "wtFQZIa2VXL", "value": assign_value_if_NaN(CBP_Lymphocytes)},
            {"dataElement": "I54JSDTreyw", "value": assign_value_if_NaN(CBP_Neutrophils)},
            {"dataElement": "H798H80HF1D", "value": assign_value_if_NaN(CBP_Basophils)},
            {"dataElement": "wwZMbKetAqZ", "value": assign_value_if_NaN(CBP_Eosinophils)},
            {"dataElement": "LASLHlcXqVj", "value": assign_value_if_NaN(CBP_MCV)},
            {"dataElement": "s9R03jgGnuW", "value": assign_value_if_NaN(CBP_MCH)},
            {"dataElement": "QsA3HQOcnVI", "value": assign_value_if_NaN(CBP_MCHC)},
            {"dataElement": "KVpFzgFVFh7", "value": assign_value_if_NaN(CBP_Hematocrit)},
            {"dataElement": "S5TC82kQSGw", "value": assign_value_if_NaN(CBP_Platelet_Count)},
            {"dataElement": "ZkshCX0lVYr", "value": assign_value_if_NaN(CBP_Total_Leucocyte_Count)},
            {"dataElement": "VQG7KG7g2Yl", "value": assign_value_if_NaN(Widal_Test)},
            {"dataElement": "KQH5TX5d9d8", "value": assign_value_if_NaN(Sputum_AFB_Test)},
            {"dataElement": "RXFfqpniXFK", "value": assign_value_if_NaN(Sickle_Cell_Disease_Test)},
            {"dataElement": "BCek0KLeBgf", "value": assign_value_if_NaN(HBsAg)},
            {"dataElement": "QSv07DHSjo9", "value": assign_value_if_NaN(Complete_Urine_Examination)},
            {"dataElement": "Oqzyv0ohQMi", "value": assign_value_if_NaN(Complete_Urine_Examination_Total_Leucocyte_Count)},
            {"dataElement": "MNOfTdeq13P", "value": assign_value_if_NaN(Complete_Urine_Examination_Urine_for_Nitrite)},
            {"dataElement": "sCtzFnTrWHJ", "value": assign_value_if_NaN(Chikungunya)},
            {"dataElement": "SgDu8sd2lTd", "value": assign_value_if_NaN(Hb_Electrophoresis)},
            {"dataElement": "yUqnLiBqsE7", "value": assign_value_if_NaN(Dengue_NS1_Antigen)},
            {"dataElement": "lzOJUUFBNDW", "value": assign_value_if_NaN(Dengue_Antibody_Test)},
            {"dataElement": "B3JviFEVmbG", "value": assign_value_if_NaN(HIV1_HIV2_RDT)},
            {"dataElement": "UavTdko3A6n", "value": assign_value_if_NaN(Visual_Acuity_Test)},
            {"dataElement": "bN7qCYfCDc3", "value": assign_value_if_NaN(Blood_Group)},
            {"dataElement": "pK5GxqNaAeE", "value": assign_value_if_NaN(VDRL_Test)},
            {"dataElement": "E8FR6XWH0JH", "value": assign_value_if_NaN(Syphilis)},
            {"dataElement": "azZFm9OxSac", "value": assign_value_if_NaN(Serum_Uric_Acid)},
            {"dataElement": "TBA2fG0zmW2", "value": assign_value_if_NaN(Serum_Total_Cholesterol)},
            {"dataElement": "Trt8PKKUfQT", "value": assign_value_if_NaN(Hepatitis_B)},
            {"dataElement": "xPuq16liQ82", "value": assign_value_if_NaN(Hepatitis_C)},
            {"dataElement": "hGZ4pC3EY6c", "value": assign_value_if_NaN(ESR)},
            {"dataElement": "nCMJQKramRa", "value": assign_value_if_NaN(RBS_Status)}
        ]
        
    }

    #print( f" event_payload length . { len(event_payload) }" )
    #print(f"event_payload: {event_payload}" )

    return event_payload


def assign_value_if_NaN(value):
    if pd.notnull(value):
        if isinstance(value, int):
            return value
        elif isinstance(value, float):
            return value
        elif value == 'NULL':
            return ""
        else:
            return str(value)
    
    else:
        return ""


def create_events_in_dhis2(multiple_events_payload, BeneficiaryRegID, Visitcode):
    #print(f"multiple_events_payload : {multiple_events_payload}")

    if multiple_events_payload is not None:
        #print( f" event_payload orgUnit . { multiple_events_payload }" )
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
            print(f"Events created successfully. Visitcode : {Visitcode} . BeneficiaryRegID : {BeneficiaryRegID}. Event count: {event_count} . imported event : {event_uid}")
            logging.info(f"Events created successfully. Visitcode : {Visitcode} . BeneficiaryRegID : {BeneficiaryRegID}. Event count: {event_count}. imported event : {event_uid}")
            #logging.info(f"Event created successfully . BenVisitID : {BenVisitID} . BeneficiaryRegID : {BeneficiaryRegID}. Event count: {event_count}. Event uid: {event_uid}" )
            #logging.info("MySQL connection closed")

        else:
            print(f"Failed to create events. Error: {response.text}")
            logging.error(f"Failed to create events . Visitcode : {Visitcode} . BeneficiaryRegID : {BeneficiaryRegID}. Status code: {response.status_code} . error details: {response.json()}")


def construct_xlsx_event_payload(trackedEntityInstance, orgUnit, Visitcode, BenVisitID, BeneficiaryRegID,
                       VisitNo, CreatedDate, vanid, AgeOnVisit, VisitReason, VisitCategory, PregnancyStatus,
                       Referal_Visitcode, referredToInstituteName, referralreason,ProvisionalDiagnosis,
                       phyanthropometry_bmi, nurse_rbs, Weight_Kg, Height_cm, WaistCircumference_cm,
                       Temperature, SystolicBP_1stReading, DiastolicBP_1stReading, ComorbidCondition_Fulltext,
                       Comobrid_Diabetes,Comobrid_Hypertension,Comobrid_Asthma,Comobrid_Epilepsy,Comobrid_Heart_Disease,
                       Comobrid_Kidney_Disease,Comobrid_Sickle_cell,Labtest_Prescribed, Drug_Prescribedcode, Drug_Dispensecode,
                       diagnosisprovided_full_text, DiagnosisProvided1, NCD_Condition, ncd_condition_full_text,
                       PulseRate, spo2, feto_Visitcode,TestName, GenericDrugName, Labtest_Done_Visitcode,Total_lab_test,
                       Random_Blood_Sugar, Hemoglobin, UrineAlbumin, UrineSugar, Urine_Pregnancy_test, Malaria, ECG, HbA1c,
                       Liver_Function_Test, Liverfunctiontest_Direct_Bilirubin, Liverfunctiontest_SGPT, Liverfunctiontest_SGOT,
                       Liverfunctiontest_Total_Serum_Bilirubin, Liverfunctiontest_Blood_Urea, Liverfunctiontest_Serum_Creatinine,
                       Renal_function_test, Renalfunctiontest_Serum_Creatinine, Renalfunctiontest_Blood_Urea,
                       Lipid_profile, Lipidprofile_Serum_Total_Cholesterol, Lipidprofile_Serum_HDL, Lipidprofile_LDL, Lipidprofile_Serum_Triglycerides,
                       Post_Lunch_Blood_Sugar, Fasting_Blood_Sugar, Complete_Blood_Picture, CBP_ESR, CBP_Monocytes,
                       CBP_Hemoglobin, CBP_RBC, CBP_Lymphocytes, CBP_Neutrophils, CBP_Basophils, CBP_Eosinophils, CBP_MCV,
                       CBP_MCH, CBP_MCHC, CBP_Hematocrit, CBP_Platelet_Count, CBP_Total_Leucocyte_Count, Widal_Test,
                       Sputum_AFB_Test, Sickle_Cell_Disease_Test, HBsAg, Complete_Urine_Examination,
                       Complete_Urine_Examination_Total_Leucocyte_Count, Complete_Urine_Examination_Urine_for_Nitrite,
                       Chikungunya, Hb_Electrophoresis, Dengue_NS1_Antigen, Dengue_Antibody_Test,
                       HIV1_HIV2_RDT, Visual_Acuity_Test, Blood_Group, VDRL_Test, Syphilis, Serum_Uric_Acid, Serum_Total_Cholesterol,
                       Hepatitis_B, Hepatitis_C, ESR, RBS_Status ):
    

    eventDate = CreatedDate.strftime("%Y-%m-%d")
    event_payload = {
        #"event" : event,
        "program": "NMGbY2nXCKu",
        "orgUnit": orgUnit,
        "eventDate": eventDate,
        "programStage": "qJbHjQBuG3G",
        "status": "ACTIVE",
        "trackedEntityInstance": trackedEntityInstance,
        "dataValues": [
            {"dataElement": "QRE1IBSOKdE", "value": assign_value_if_NaN(Visitcode)},
            {"dataElement": "Q7aA5HvvV7L", "value": assign_value_if_NaN(BenVisitID)},
            {"dataElement": "hzYStHHLxQy", "value": assign_value_if_NaN(VisitNo)},
            {"dataElement": "P5a5E6m8llj", "value": assign_value_if_NaN(AgeOnVisit)},
            {"dataElement": "GwHcyOdg4CD", "value": assign_value_if_NaN(VisitReason)},
            {"dataElement": "oTsj7lfUVgo", "value": assign_value_if_NaN(VisitCategory)},
            {"dataElement": "s3afEOkQTlg", "value": assign_value_if_NaN(PregnancyStatus)},
            {"dataElement": "AKMkMnWNiG1", "value": assign_value_if_NaN(Referal_Visitcode)},
            {"dataElement": "KtoABiKQ6lK", "value": assign_value_if_NaN(referredToInstituteName)},
            {"dataElement": "ryiIUM1S8ar", "value": assign_value_if_NaN(referralreason)},
            {"dataElement": "wBL3WAU2bTC", "value": assign_value_if_NaN(ProvisionalDiagnosis)},
            {"dataElement": "pohCVodbTm6", "value": assign_value_if_NaN(phyanthropometry_bmi)},
            {"dataElement": "s7vpadfqfmS", "value": assign_value_if_NaN(nurse_rbs)},
            {"dataElement": "vRc7DmJMEQI", "value": assign_value_if_NaN(Weight_Kg)},  
            {"dataElement": "vw8R2gyAuPo", "value": assign_value_if_NaN(Height_cm)},     
            {"dataElement": "QV2NY50zE1E", "value": assign_value_if_NaN(WaistCircumference_cm)},    
            {"dataElement": "prXoT8ZJdiv", "value": assign_value_if_NaN(Temperature)}, 
            {"dataElement": "X8UNYvbZ9wV", "value": assign_value_if_NaN(SystolicBP_1stReading)},
            {"dataElement": "wwy7WCpuqfv", "value": assign_value_if_NaN(DiastolicBP_1stReading)},
            {"dataElement": "rgcw6SjzDYn", "value": assign_value_if_NaN(ComorbidCondition_Fulltext)},
            {"dataElement": "TttgfrMMSby", "value": assign_value_if_NaN(Comobrid_Diabetes)},
            {"dataElement": "LmmrcssSi8F", "value": assign_value_if_NaN(Comobrid_Hypertension)},
            {"dataElement": "xd4Qt4AM213", "value": assign_value_if_NaN(Comobrid_Asthma)},
            {"dataElement": "WfnpRqRWEHM", "value": assign_value_if_NaN(Comobrid_Epilepsy)},
            {"dataElement": "SuSHF1kefrG", "value": assign_value_if_NaN(Comobrid_Heart_Disease)},
            {"dataElement": "tgQbzqXDNRP", "value": assign_value_if_NaN(Comobrid_Kidney_Disease)},
            {"dataElement": "FyhwhFUY0nh", "value": assign_value_if_NaN(Comobrid_Sickle_cell)},
            {"dataElement": "SEWpIBXOVJr", "value": assign_value_if_NaN(Labtest_Prescribed)},
            {"dataElement": "pgdoeXKo0GL", "value": assign_value_if_NaN(Drug_Prescribedcode)},
            {"dataElement": "wH98g3BPtD1", "value": assign_value_if_NaN(Drug_Dispensecode)},
            {"dataElement": "XppQ0DsgMEF", "value": assign_value_if_NaN(diagnosisprovided_full_text)},
            {"dataElement": "d5Nyb78pT99", "value": assign_value_if_NaN(DiagnosisProvided1)} ,        
            {"dataElement": "fa4AJy44Uhx", "value": assign_value_if_NaN(NCD_Condition)},
            {"dataElement": "NcOvQWsZFuU", "value": assign_value_if_NaN(ncd_condition_full_text)},
            {"dataElement": "zgCKfBhHMap", "value": assign_value_if_NaN(PulseRate)},
            {"dataElement": "kT0JD27zJmU", "value": assign_value_if_NaN(spo2)},
            {"dataElement": "t61yi6jTQpa", "value": assign_value_if_NaN(feto_Visitcode)},
            {"dataElement": "fgo6djgo0Nn", "value": assign_value_if_NaN(TestName)},
            {"dataElement": "nBSZtCvhfFi", "value": assign_value_if_NaN(GenericDrugName)},
            {"dataElement": "E3ObN0pnxhJ", "value": assign_value_if_NaN(Labtest_Done_Visitcode)},
            {"dataElement": "lWvLH2vpEGU", "value": assign_value_if_NaN(Total_lab_test)},
            {"dataElement": "erQc3s2U1RN", "value": assign_value_if_NaN(Random_Blood_Sugar)},
            {"dataElement": "P73ZGr9cIWh", "value": assign_value_if_NaN(Hemoglobin)},
            {"dataElement": "WwbiEklafqD", "value": assign_value_if_NaN(UrineAlbumin)},
            {"dataElement": "C8haFJv6IYE", "value": assign_value_if_NaN(UrineSugar)},
            {"dataElement": "bxAncSyrRwq", "value": assign_value_if_NaN(Urine_Pregnancy_test)},
            {"dataElement": "O3zLLcKw6Zs", "value": assign_value_if_NaN(Malaria)},
            {"dataElement": "ppIBftFjyvg", "value": assign_value_if_NaN(ECG)},
            {"dataElement": "VXJSZCJECMl", "value": assign_value_if_NaN(HbA1c)},
            {"dataElement": "wQXTxsIcrUh", "value": assign_value_if_NaN(Liver_Function_Test)},
            {"dataElement": "KUbWxjd1Pn2", "value": assign_value_if_NaN(Liverfunctiontest_Direct_Bilirubin)},
            {"dataElement": "zrcWf9wrb7Q", "value": assign_value_if_NaN(Liverfunctiontest_SGPT)},
            {"dataElement": "QssPLOEFFLv", "value": assign_value_if_NaN(Liverfunctiontest_SGOT)},
            {"dataElement": "YUT6t2rf4As", "value": assign_value_if_NaN(Liverfunctiontest_Total_Serum_Bilirubin)},
            {"dataElement": "N6QoKvXeYE9", "value": assign_value_if_NaN(Liverfunctiontest_Blood_Urea)},
            {"dataElement": "k7Jcp85dGeU", "value": assign_value_if_NaN(Liverfunctiontest_Serum_Creatinine)},
            {"dataElement": "Qc5M9bwj9be", "value": assign_value_if_NaN(Renal_function_test)},
            {"dataElement": "PgIxHAG8tKJ", "value": assign_value_if_NaN(Renalfunctiontest_Serum_Creatinine)},
            {"dataElement": "N386Wicr2BF", "value": assign_value_if_NaN(Renalfunctiontest_Blood_Urea)},
            {"dataElement": "f4RwwhAYsPG", "value": assign_value_if_NaN(Lipid_profile)},
            {"dataElement": "BouZJY2f9ci", "value": assign_value_if_NaN(Lipidprofile_Serum_Total_Cholesterol)},
            {"dataElement": "U9HmdhXbmOE", "value": assign_value_if_NaN(Lipidprofile_Serum_HDL)},
            {"dataElement": "zFpoX3vUfYz", "value": assign_value_if_NaN(Lipidprofile_LDL)},
            {"dataElement": "lfybIrKEtug", "value": assign_value_if_NaN(Lipidprofile_Serum_Triglycerides)},
            {"dataElement": "XigK2YJCJeA", "value": assign_value_if_NaN(Post_Lunch_Blood_Sugar)},
            {"dataElement": "oTTHBvI4lCR", "value": assign_value_if_NaN(Fasting_Blood_Sugar)},
            {"dataElement": "oulQE5uBdPE", "value": assign_value_if_NaN(Complete_Blood_Picture)},
            {"dataElement": "GuWsng25Ejm", "value": assign_value_if_NaN(CBP_ESR)},
            {"dataElement": "EpDktJlqflN", "value": assign_value_if_NaN(CBP_Monocytes)},
            {"dataElement": "jb41MTR49ud", "value": assign_value_if_NaN(CBP_Hemoglobin)},
            {"dataElement": "usmFpkYjuFV", "value": assign_value_if_NaN(CBP_RBC)},
            {"dataElement": "wtFQZIa2VXL", "value": assign_value_if_NaN(CBP_Lymphocytes)},
            {"dataElement": "I54JSDTreyw", "value": assign_value_if_NaN(CBP_Neutrophils)},
            {"dataElement": "H798H80HF1D", "value": assign_value_if_NaN(CBP_Basophils)},
            {"dataElement": "wwZMbKetAqZ", "value": assign_value_if_NaN(CBP_Eosinophils)},
            {"dataElement": "LASLHlcXqVj", "value": assign_value_if_NaN(CBP_MCV)},
            {"dataElement": "s9R03jgGnuW", "value": assign_value_if_NaN(CBP_MCH)},
            {"dataElement": "QsA3HQOcnVI", "value": assign_value_if_NaN(CBP_MCHC)},
            {"dataElement": "KVpFzgFVFh7", "value": assign_value_if_NaN(CBP_Hematocrit)},
            {"dataElement": "S5TC82kQSGw", "value": assign_value_if_NaN(CBP_Platelet_Count)},
            {"dataElement": "ZkshCX0lVYr", "value": assign_value_if_NaN(CBP_Total_Leucocyte_Count)},
            {"dataElement": "VQG7KG7g2Yl", "value": assign_value_if_NaN(Widal_Test)},
            {"dataElement": "KQH5TX5d9d8", "value": assign_value_if_NaN(Sputum_AFB_Test)},
            {"dataElement": "RXFfqpniXFK", "value": assign_value_if_NaN(Sickle_Cell_Disease_Test)},
            {"dataElement": "BCek0KLeBgf", "value": assign_value_if_NaN(HBsAg)},
            {"dataElement": "QSv07DHSjo9", "value": assign_value_if_NaN(Complete_Urine_Examination)},
            {"dataElement": "Oqzyv0ohQMi", "value": assign_value_if_NaN(Complete_Urine_Examination_Total_Leucocyte_Count)},
            {"dataElement": "MNOfTdeq13P", "value": assign_value_if_NaN(Complete_Urine_Examination_Urine_for_Nitrite)},
            {"dataElement": "sCtzFnTrWHJ", "value": assign_value_if_NaN(Chikungunya)},
            {"dataElement": "SgDu8sd2lTd", "value": assign_value_if_NaN(Hb_Electrophoresis)},
            {"dataElement": "yUqnLiBqsE7", "value": assign_value_if_NaN(Dengue_NS1_Antigen)},
            {"dataElement": "lzOJUUFBNDW", "value": assign_value_if_NaN(Dengue_Antibody_Test)},
            {"dataElement": "B3JviFEVmbG", "value": assign_value_if_NaN(HIV1_HIV2_RDT)},
            {"dataElement": "UavTdko3A6n", "value": assign_value_if_NaN(Visual_Acuity_Test)},
            {"dataElement": "bN7qCYfCDc3", "value": assign_value_if_NaN(Blood_Group)},
            {"dataElement": "pK5GxqNaAeE", "value": assign_value_if_NaN(VDRL_Test)},
            {"dataElement": "E8FR6XWH0JH", "value": assign_value_if_NaN(Syphilis)},
            {"dataElement": "azZFm9OxSac", "value": assign_value_if_NaN(Serum_Uric_Acid)},
            {"dataElement": "TBA2fG0zmW2", "value": assign_value_if_NaN(Serum_Total_Cholesterol)},
            {"dataElement": "Trt8PKKUfQT", "value": assign_value_if_NaN(Hepatitis_B)},
            {"dataElement": "xPuq16liQ82", "value": assign_value_if_NaN(Hepatitis_C)},
            {"dataElement": "hGZ4pC3EY6c", "value": assign_value_if_NaN(ESR)},
            {"dataElement": "nCMJQKramRa", "value": assign_value_if_NaN(RBS_Status)}
        ]
        
    }

    #print(f"event_payload: {event_payload}" )

    return event_payload

'''
def assign_value_if_NaN(value):
    if pd.notnull(value):
        if isinstance(value, int):
            return value
        elif isinstance(value, float):
            return value
        else:
            return value.strip()
    else:
        return ""
'''

def remove_space_if_NaN(value):
    if pd.notnull(value):
        return value.strip()
    else:
        return ""    
    
def create_events_in_dhis2_xlsx(multiple_events_payload, BeneficiaryRegID, Visitcode, row_no):
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
        print(f"Events created successfully. Row No : {row_no} . BeneficiaryRegID : {BeneficiaryRegID} . VisitCode : {Visitcode} . BeneficiaryRegID : {BeneficiaryRegID}. Event count: {event_count}. imported event : {event_uid}")
        logging.info(f"Events created successfully. Row No : {row_no} . BeneficiaryRegID : {BeneficiaryRegID} . VisitCode : {Visitcode} . Event count: {event_count}. imported event : {event_uid}")
        #logging.info(f"Event created successfully . BenVisitID : {BenVisitID} . BeneficiaryRegID : {BeneficiaryRegID}. Event count: {event_count}. Event uid: {event_uid}" )
        #logging.info("MySQL connection closed")

    else:
        print(f"Failed to create events. Error: {response.text}")
        logging.error(f"Failed to create events . Row No : {row_no} . BeneficiaryRegID : {BeneficiaryRegID} . VisitCode : {Visitcode} . Status code: {response.status_code} . error details: {response.json()} .Error: {response.text}")
