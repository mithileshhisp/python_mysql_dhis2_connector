# main_script.py

# Author: sourabhB
import logging
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from dhis2_api_interaction import get_org_unit_and_option_data, create_enrollment, check_existing_tei
from database_connection import connect_to_mysql

logging.basicConfig(filename='enrollment.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

num_threads = 20

def create_enrollment_for_row(row):
    BeneficiaryRegID, FirstName, MiddleName, LastName, Gender, DOB, VanID, CreatedDate, PermStateId, PermState, PermDistrictId, PermDistrict, PermSubDistrict, PermSubDistrictId, PermVillageId, PermVillage = row

    existing_tei = check_existing_tei(BeneficiaryRegID)

    if existing_tei:
        print(f"TEI already exists for BeneficiaryRegID {BeneficiaryRegID}. Skipping.")
        return

    org_unit_id, option_name = get_org_unit_and_option_data(PermSubDistrictId, PermVillageId)

    enrollment_data = {
        "trackedEntityType": "T10dZwFVdkz",
        "enrollmentStatus": "ACTIVE",
        "attributes": [
            {"attribute": "BGnnMn2zhe2", "value": MiddleName},
            {"attribute": "HKw3ToP2354", "value": BeneficiaryRegID},
            {"attribute": "HY3yFbdrtgv", "value": VanID},
            {"attribute": "I3E7eVo5ieh", "value": DOB},
            {"attribute": "KbHdenDCzwp", "value": Gender},
            {"attribute": "VOHkkdTcf7g", "value": option_name},
            {"attribute": "Yji5uTwhjLI", "value": FirstName},
            {"attribute": "qB2TXjT229Y", "value": LastName},
        ],
        "enrollments": [
            {
                "program": "vyQPQ07JB9M",
                "enrollmentDate": CreatedDate,
                "incidentDate": CreatedDate
            }
        ]
    }

    response = create_enrollment(enrollment_data, org_unit_id)

    if response.status_code == 200:
        logging.info(f"Enrollment created successfully for BeneficiaryRegID {BeneficiaryRegID}")
    else:
        logging.error(f"Failed to create enrollment for BeneficiaryRegID {BeneficiaryRegID}. Status code: {response.status_code}")

try:
    mysql_connection = connect_to_mysql()

    if mysql_connection.is_connected():
        print("Connected to MySQL database")
        mysql_cursor = mysql_connection.cursor()
        mysql_query = f"""
    SELECT
        i_ben_details.BeneficiaryRegID,
        i_ben_details.FirstName,
        i_ben_details.MiddleName,
        i_ben_details.LastName,
        i_ben_details.Gender,
        IF(i_ben_details.DOB IS NOT NULL, DATE_FORMAT(i_ben_details.DOB, '%Y-01-01'), NULL) AS DOB,
        i_ben_details.VanID,
        i_ben_details.CreatedDate,
        i_ben_address.PermStateId,
        i_ben_address.PermState,
        i_ben_address.PermDistrictId,
        i_ben_address.PermDistrict,
        i_ben_address.PermSubDistrict,
        i_ben_address.PermSubDistrictId,
        i_ben_address.PermVillageId,
        i_ben_address.PermVillage
    FROM i_beneficiarydetails i_ben_details
    INNER JOIN i_beneficiarymapping i_ben_mapping ON i_ben_mapping.BenRegId = i_ben_details.BeneficiaryRegID
    INNER JOIN i_beneficiaryaddress i_ben_address ON i_ben_address.BenAddressID = i_ben_mapping.BenAddressId
    WHERE i_ben_details.BeneficiaryRegID IS NOT NULL;
"""
        mysql_cursor.execute(mysql_query)
        mysql_rows = mysql_cursor.fetchall()
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            for row in mysql_rows:
                executor.submit(create_enrollment_for_row, row)

except Exception as e:
    logging.error(f"Error: {str(e)}")
finally:
    if 'mysql_cursor' in locals():
        mysql_cursor.close()
    if 'mysql_connection' in locals() and mysql_connection.is_connected():
        mysql_connection.close()
        logging.info("MySQL connection closed")
