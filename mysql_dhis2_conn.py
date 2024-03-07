import mysql.connector
import requests
from datetime import datetime
from constants import  DHIS2_API_URL, DHIS2_AUTH
from utils import (
    configure_logging,
    log_info,
    log_error,
)
mysql_host = '****'
mysql_port = ****
mysql_database = '****'
mysql_user = '****'
mysql_password = '****'
dhis2_api_url = "*****"
dhis2_username = "admin"
dhis2_password = "*****"



#thisdict = {}
#thisdict = get_dhis2_orgunit_level4()
#print(thisdict["year"])
#thisdict["123"] = "atatatta"

#print(thisdict["123"])
#print(thisdict['688'])
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

def assign_value_if_not_null(value):
    if value is not None and value != "null":
        return value
    else:
        return ""
try:
    mysql_connection = mysql.connector.connect(
        host=mysql_host,
        port=mysql_port,
        database=mysql_database,
        user=mysql_user,
        password=mysql_password
    )





    orgUnitMap = {}
    orgUnitMap = get_dhis2_orgunit_level4()
    #print(orgUnitMap)
    #print(orgUnitMap['152'])
    #print(orgUnitMap['6309'])
    print(orgUnitMap['534'])
    print( len( orgUnitMap ) )

    if mysql_connection.is_connected():
        print("Connected to MySQL database")
        mysql_cursor = mysql_connection.cursor()
        mysql_query = """
SELECT i_ben_details.BeneficiaryRegID, i_ben_details.FirstName,i_ben_details.MiddleName,
i_ben_details.LastName,i_ben_details.DOB,i_ben_details.VanID, i_ben_details.CreatedDate,
i_ben_address.PermSubDistrictId,i_ben_address.PermVillageId,i_ben_address.PermVillage
FROM i_beneficiarydetails i_ben_details
INNER JOIN i_beneficiarymapping i_ben_mapping ON i_ben_mapping.BenRegId = i_ben_details.BeneficiaryRegID
INNER JOIN i_beneficiaryaddress i_ben_address ON i_ben_address.BenAddressID = i_ben_mapping.BenAddressId
WHERE i_ben_details.BeneficiaryRegID IS NOT NULL AND i_ben_address.PermStateId IS NOT NULL
AND i_ben_address.PermDistrictId IS NOT NULL AND i_ben_address.PermSubDistrictId IS NOT NULL
LIMIT 10;
        """


        mysql_cursor.execute(mysql_query)
        mysql_rows = mysql_cursor.fetchall()


        for mysql_row in mysql_rows:

            #BeneficiaryRegID, FirstName, MiddleName,LastName,DOB,VanID,CreatedDate,
            #PermStateId,PermState,PermDistrictId,PermDistrict,PermSubDistrict,PermSubDistrictId,
            #PermVillageId,PermVillage = mysql_row

            #print( assign_value_if_not_null(mysql_row[0]), assign_value_if_not_null(mysql_row[1]), assign_value_if_not_null(mysql_row[2]), assign_value_if_not_null(mysql_row[3]) )
            print(mysql_row[7])
            print(orgUnitMap[mysql_row[7]])
            print(orgUnitMap[ '534' ])

            #dhis2_org_unit_url = f"{dhis2_api_url}?filter=code:eq:{state_code}&fields=id,name,shortName,openingDate"
            #print("org url--",dhis2_org_unit_url)
            #print("state--",state_name)
            #response = requests.get(dhis2_org_unit_url, auth=("dhis2_username", "dhis2_password"))
            """
            if response.status_code == 200:
                org_units = response.json().get("organisationUnits")
                if org_units:
                    org_unit_id = org_units[0]["id"]
                    short_name=org_units[0]["shortName"]
                    opening_date=org_units[0]["openingDate"]
                    name_org=org_units[0]["name"]
                    update_url = f"{dhis2_api_url}/{org_unit_id}"
                    payload = {
                        "name": name_org,
                        "code":state_code,
                        "parent": {"id": "NQjElqVFZTm"},
                        "shortName": short_name,
                        "openingDate": opening_date,
                        "attributeValues": [{"attribute": {"id": "MHGdoVG6E5S"},"value": govt_state_id}]
                    }
                    response = requests.put(
                        update_url,
                        json=payload,
                        auth=("dhis2_username", dhis2_password)
                    )

                    if response.status_code == 200:
                        print(f"Updated org unit {org_unit_id} with GovtStateID: {govt_state_id}")
                    else:
                        print(f"Failed to update org unit {org_unit_id}. Status code: {response.status_code}")
                else:
                    print(f"No matching organization unit found for code: {state_code}")

            else:
                print(f"Failed to retrieve organization unit. Status code: {response.status_code}")
                """
except Exception as e:
    print(f"Error: {str(e)}")
finally:
    if 'mysql_cursor' in locals():
        mysql_cursor.close()
    if 'mysql_connection' in locals() and mysql_connection.is_connected():
        mysql_connection.close()
        print("MySQL connection closed")


