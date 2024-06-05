#import mysql_connection
#import dhis2_integration
from dhis2_api_interaction import get_org_unit_data, get_tei_data, construct_event_payload, create_events_in_dhis2
import database_connection
import logging
import pandas as pd
from database_connection import connect_to_mysql

# MySQL connection parameters
#mysql_host = '*****'
#mysql_port = 1234
#mysql_database = '******'
#mysql_user = '******'
#mysql_password = '*******'

# DHIS2 API parameters
#dhis2_base_url = '********'
#dhis2_username = '********'
#dhis2_password = '********'

from constants import LOG_FILE_EVENT

logging.basicConfig(filename=LOG_FILE_EVENT, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# logging.basicConfig(filename='bayer_event.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

mysql_connection = connect_to_mysql()
#mysql_conn = database_connection.establish_mysql_connection(mysql_host, mysql_port, mysql_user, mysql_password, mysql_database)

# logging.info("MySQL connection closed")
print("Connected to MySQL database")
logging.info("Connected to MySQL database")
cursor = mysql_connection.cursor()

results = database_connection.fetch_mysql_data(cursor)

mysql_connection.close()

logging.info("MySQL connection closed")

tei_data_cache = {}
events_by_reg_id = {}


for result in results:
    BenVisitID, BeneficiaryRegID, VisitNo, CreatedDate, VanID, AgeOnVisit, VisitReason, VisitCategory, RCHID, ProvisionalDiagnosis, SystolicBP_1stReading, DiastolicBP_1stReading, Status, referredToInstituteName, ProcedureName, NCD_Condition1, NCD_Condition2, NCD_Condition3, NCD_Condition4, DiagnosisProvided1, DiagnosisProvided2, DiagnosisProvided3, DiagnosisProvided4, DiagnosisProvided5 = result

    CreatedDate = CreatedDate.strftime("%Y-%m-%d")
    
    org_unit_id = get_org_unit_data(VanID)

    tei_data = get_tei_data(org_unit_id, BeneficiaryRegID, tei_data_cache)

    if tei_data:
        event_payload = construct_event_payload(tei_data, CreatedDate,
            BenVisitID, BeneficiaryRegID, VisitNo, AgeOnVisit, 
            VisitReason, VisitCategory, RCHID, ProvisionalDiagnosis, 
            SystolicBP_1stReading, DiastolicBP_1stReading, Status, 
            referredToInstituteName, ProcedureName, NCD_Condition1, NCD_Condition2, 
            NCD_Condition3, NCD_Condition4, DiagnosisProvided1, DiagnosisProvided2, 
            DiagnosisProvided3, DiagnosisProvided4, DiagnosisProvided5 )


        #if BeneficiaryRegID in events_by_reg_id:
            #events_by_reg_id[BeneficiaryRegID].append(event_payload)
        #else:
            #events_by_reg_id[BeneficiaryRegID] = [event_payload]
            
        #print(f"events_by_reg_id : {events_by_reg_id}")

#for reg_id, events in events_by_reg_id.items():
    #multiple_events_payload = {
        #"events": events
    #}

    #dhis2_api_interaction.create_events_in_dhis2(dhis2_base_url, dhis2_username, dhis2_password, multiple_events_payload,BeneficiaryRegID)
    create_events_in_dhis2( event_payload,BeneficiaryRegID, BenVisitID )
