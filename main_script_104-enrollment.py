# main_script.py

# Author: sourabhB
import logging
# import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from dhis2_api_interaction import get_org_unit_data, create_enrollment, check_existing_tei
from database_connection import connect_to_mysql

logging.basicConfig(filename='104_enrollment.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

num_threads = 20

def assign_value_if_not_null(value):
    if value is not None and value != "null":
        return value
    else:
        return ""

def create_enrollment_for_row(row):
    BeneficiaryID, MappingBenRegId, BeneficiaryRegID, CreatedDate, FirstName, MiddleName, LastName, Gender, DOB, VanID, PermSubDistrictId = row

    CreatedDate = CreatedDate.strftime("%Y-%m-%d")

    existing_tei = check_existing_tei(MappingBenRegId)

    if existing_tei:
        print(f"TEI already exists for BeneficiaryRegID {MappingBenRegId}. Skipping.")
        logging.info(f"TEI already exists for BeneficiaryRegID {MappingBenRegId}. Skipping.")
        return

    # org_unit_id, option_name = get_org_unit_and_option_data(PermSubDistrictId, PermVillageId)
    org_unit_id = get_org_unit_data(PermSubDistrictId)

    enrollment_data = {
        "trackedEntityType": "T10dZwFVdkz",
        "orgUnit": org_unit_id,
        "attributes": [
            {"attribute": "pQLwsC8cu9R", "value": assign_value_if_not_null(BeneficiaryID)},
            {"attribute": "HKw3ToP2354", "value": assign_value_if_not_null(MappingBenRegId)},
            {"attribute": "bkMqkldhlhA", "value": assign_value_if_not_null(BeneficiaryRegID)},
            {"attribute": "Yji5uTwhjLI", "value": assign_value_if_not_null(FirstName)},
            {"attribute": "BGnnMn2zhe2", "value": assign_value_if_not_null(MiddleName)},
            {"attribute": "qB2TXjT229Y", "value": assign_value_if_not_null(LastName)},
            {"attribute": "KbHdenDCzwp", "value": assign_value_if_not_null(Gender)},
            {"attribute": "I3E7eVo5ieh", "value": assign_value_if_not_null(DOB)},
            {"attribute": "HY3yFbdrtgv", "value": assign_value_if_not_null(VanID)}
        ],
        "enrollments": [
            {
                "status": "ACTIVE",
                "program": "vyQPQ07JB9M",
                "enrollmentDate": CreatedDate,
                "incidentDate": CreatedDate
            }
        ]
    }
    response = create_enrollment(enrollment_data, org_unit_id,CreatedDate)
    #print(f"enrollment_response {response} " )

    if response.status_code == 200:
        logging.info(f"Enrollment created successfully for BeneficiaryRegID {MappingBenRegId}")
        print(f"Enrollment created successfully for BeneficiaryRegID {MappingBenRegId}")
    else:
        logging.error(f"Failed to create enrollment for BeneficiaryRegID {MappingBenRegId}. Status code: {response.status_code} . error details: {response.json()}")

try:
    mysql_connection = connect_to_mysql()

    if mysql_connection.is_connected():
        print("104 enrollment query")
        print("Connected to MySQL database")
        mysql_cursor = mysql_connection.cursor()
        mysql_query = f"""

        SELECT mb.BeneficiaryID,i_ben_mapping.BenRegId AS mappingBenRegId, i_ben_details.BeneficiaryRegID,
        CAST(i_ben_mapping.CreatedDate AS DATE) As CreatedDate,i_ben_details.FirstName,
        i_ben_details.MiddleName, i_ben_details.LastName, i_ben_details.Gender,

        IF(i_ben_details.DOB IS NOT NULL,DATE_FORMAT(i_ben_details.DOB, '%Y-01-01'), NULL) AS DOB,
        i_ben_mapping.VanID,i_ben_address.PermSubDistrictId

        FROM db_identity.i_beneficiarymapping i_ben_mapping

        INNER join db_identity.m_beneficiaryregidmapping mb on mb.BenRegId=i_ben_mapping.BenRegId
        INNER JOIN db_identity.i_beneficiarydetails i_ben_details ON i_ben_details.BeneficiaryDetailsId = i_ben_mapping.BenDetailsId
        INNER JOIN db_identity.i_beneficiaryaddress i_ben_address ON i_ben_address.BenAddressID = i_ben_mapping.BenAddressId

        WHERE i_ben_mapping.BenRegId IS NOT NULL AND i_ben_address.PermStateId IS NOT NULL
        AND i_ben_address.PermDistrictId IS NOT NULL AND i_ben_address.PermSubDistrictId IS NOT NULL
        AND i_ben_mapping.VanID = 3 and
        i_ben_mapping.CreatedDate between '2024-01-01 00:00:00' and '2024-03-31 23:59:59'
        order by i_ben_mapping.BenRegId ASC;

        """
        mysql_cursor.execute(mysql_query)
        mysql_rows = mysql_cursor.fetchall()
        for row in mysql_rows:
            create_enrollment_for_row(row)


        #with ThreadPoolExecutor(max_workers=num_threads) as executor:
            #for row in mysql_rows:
                #executor.submit(create_enrollment_for_row, row)

except Exception as e:
    logging.error(f"Error: {str(e)}")
finally:
    if 'mysql_cursor' in locals():
        mysql_cursor.close()
    if 'mysql_connection' in locals() and mysql_connection.is_connected():
        mysql_connection.close()
        logging.info("MySQL connection closed")
