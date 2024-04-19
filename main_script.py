import mysql_connection
import dhis2_integration

# MySQL connection parameters
mysql_host = '####'
mysql_port = 121
mysql_database = '###'
mysql_user = '###'
mysql_password = '###'

# DHIS2 API parameters
dhis2_base_url = 'https://links.hispindia.org/'
dhis2_username = ''
dhis2_password = ''

mysql_conn = mysql_connection.establish_mysql_connection(mysql_host, mysql_port, mysql_user, mysql_password, mysql_database)
cursor = mysql_conn.cursor()

results = mysql_connection.fetch_mysql_data(cursor)
mysql_conn.close()

tei_data_cache = {}
events_by_reg_id = {}

for result in results:
    BenCallID, BeneficiaryRegID, CallID, PhoneNo, CallTypeID, is1097, Category, SubCategory, IsOutbound, CallTime, CallEndTime, CallDurationInSeconds, ReceivedRoleName, CreatedDate, TypeOfComplaint, CallType = result

    CreatedDate = CreatedDate.strftime("%Y-%m-%d")
    
    tei_data = dhis2_integration.get_tei_data(dhis2_base_url, dhis2_username, dhis2_password, BeneficiaryRegID, tei_data_cache)

    if tei_data:
        event_payload = dhis2_integration.construct_event_payload(
            tei_data, CreatedDate, BenCallID, CallType, CallTime, CallEndTime, CallDurationInSeconds, ReceivedRoleName, IsOutbound, Category, SubCategory
        )

        if BeneficiaryRegID in events_by_reg_id:
            events_by_reg_id[BeneficiaryRegID].append(event_payload)
        else:
            events_by_reg_id[BeneficiaryRegID] = [event_payload]

for reg_id, events in events_by_reg_id.items():
    multiple_events_payload = {
        "events": events
    }

    dhis2_integration.create_events_in_dhis2(dhis2_base_url, dhis2_username, dhis2_password, multiple_events_payload)
