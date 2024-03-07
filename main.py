import database_operations
import dhis2_operations

try:
    mysql_connection = database_operations.connect_to_mysql()

    if mysql_connection.is_connected():
        print("connection done")
        mysql_query = "SELECT StateName, StateCode ,GovtStateID  from m_state"

        mysql_rows = database_operations.execute_mysql_query(mysql_connection, mysql_query)
        
        for mysql_row in mysql_rows:
            state_name, state_code, govt_state_id = mysql_row

            print( state_name, state_code, govt_state_id)

            org_unit_response = dhis2_operations.get_org_unit_data(state_code)
            print("reading from dhis2--",org_unit_response[0]["name"])


            if org_unit_response.status_code == 200:
                org_units = org_unit_response.json().get("organisationUnits")
                if org_units:
                    org_unit_id = org_units[0]["id"]
                    opening_date = org_units[0]["openingDate"]
                    name_org = org_units[0]["name"]
                    update_data = {
                        "name": name_org,
                        "code": state_code,
                        "parent": {"id": "NQjElqVFZTm"},
                        "shortName": "ShortName",  
                        "openingDate": opening_date,
                        "attributeValues": [{"attribute": {"id": "MHGdoVG6E5S"}, "value": govt_state_id}]
                    }

                    update_response = dhis2_operations.update_org_unit(org_unit_id, update_data)

                    if update_response.status_code == 200:
                        print(f"Updated org unit {org_unit_id} with GovtStateID: {govt_state_id}")
                    else:
                        print(f"Failed to update org unit {org_unit_id}. Status code: {update_response.status_code}")
                else:
                    print(f"No matching organization unit found for code: {state_code}")
           

        else:
                print(f"Failed to retrieve organization unit. Status code: {org_unit_response.status_code}")


except Exception as e:
    print(f"Error: {str(e)}")

finally:
    if 'mysql_connection' in locals() and mysql_connection.is_connected():
        database_operations.close_mysql_connection(mysql_connection)
        print("MySQL connection closed")