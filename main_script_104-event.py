#import mysql_connection
#import dhis2_integration
import dhis2_api_interaction
import database_connection
import logging

# MySQL connection parameters
mysql_host = ''
mysql_port = 
mysql_database = ''
mysql_user = ''
mysql_password = ''

# DHIS2 API parameters
dhis2_base_url = ''
dhis2_username = ''
dhis2_password = ''

logging.basicConfig(filename='bayer_event.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

mysql_conn = database_connection.establish_mysql_connection(mysql_host, mysql_port, mysql_user, mysql_password, mysql_database)

# logging.info("MySQL connection closed")
print("Connected to MySQL database")
cursor = mysql_conn.cursor()

results = database_connection.fetch_mysql_data(cursor)

mysql_conn.close()
logging.info("MySQL connection closed")

tei_data_cache = {}
events_by_reg_id = {}

for result in results:
    BenCallID, CallID, BeneficiaryRegID, CreatedDate, AgeOnVisit, Is1097, IsOutbound, CategoryName, SubCategoryName, PrescriptionID, ReceivedRoleName, CallDurationInSeconds, CallType, CallGroupType, Diasease, Algorithm = result

    CreatedDate = CreatedDate.strftime("%Y-%m-%d")
    
    tei_data = dhis2_api_interaction.get_tei_data(dhis2_base_url, dhis2_username, dhis2_password, BeneficiaryRegID, tei_data_cache)

    if tei_data:
        event_payload = dhis2_api_interaction.construct_event_payload(
            tei_data, CreatedDate, BenCallID, CallID, AgeOnVisit, Is1097, IsOutbound, CategoryName, SubCategoryName, PrescriptionID, ReceivedRoleName,
            CallDurationInSeconds, CallType, CallGroupType, Algorithm )

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
    dhis2_api_interaction.create_events_in_dhis2(dhis2_base_url, dhis2_username, dhis2_password, event_payload,BeneficiaryRegID, BenVisitID)
