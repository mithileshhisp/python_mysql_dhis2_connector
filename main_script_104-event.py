#import mysql_connection
#import dhis2_integration
import dhis2_api_interaction
import database_connection
import logging
import pandas as pd
from database_connection import connect_to_mysql

# MySQL connection parameters
#mysql_host = ''
#mysql_port = 
#mysql_database = ''
#mysql_user = ''
#mysql_password = ''

# DHIS2 API parameters
dhis2_base_url = ''
dhis2_username = ''
dhis2_password = ''

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

def read_excel_to_dict(file_path):

    data = pd.read_excel(file_path)
    option_dict = {}

    for _, row in data.iterrows():
        code = row['option_code']
        #value = row['option_values'].strip()
        value = row['option_values']

        if code not in option_dict:
            #option_dict[code] = [value]
            option_dict[code] = value
        else:
            if value not in option_dict[code]:
                #option_dict[code].append(value)
                option_dict[code] = value

    return option_dict

excel_path = 'options.xlsx' 
data_dict = read_excel_to_dict(excel_path)

for result in results:
    BenCallID, CallID, BeneficiaryRegID, CreatedDate, AgeOnVisit, IsOutbound, CategoryName, SubCategoryName, PrescriptionID, ReceivedRoleName, CallDurationInSeconds, CallType, CallGroupType, Diasease = result

    CreatedDate = CreatedDate.strftime("%Y-%m-%d")
    
    tei_data = dhis2_api_interaction.get_tei_data(dhis2_base_url, dhis2_username, dhis2_password, BeneficiaryRegID, tei_data_cache)

    if tei_data:
        event_payload = dhis2_api_interaction.construct_event_payload(
            tei_data, CreatedDate, BenCallID, CallID, AgeOnVisit, IsOutbound, CategoryName, SubCategoryName, PrescriptionID, ReceivedRoleName,
            CallDurationInSeconds, CallType, CallGroupType, Diasease, data_dict )

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
    dhis2_api_interaction.create_events_in_dhis2(dhis2_base_url, dhis2_username, dhis2_password, event_payload,BeneficiaryRegID, BenCallID )
