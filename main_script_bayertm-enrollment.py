# main_script.py

# Author: mithilesh
import logging
# import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from dhis2_api_interaction import get_org_unit_data, create_enrollment, check_existing_tei
from database_connection import connect_to_mysql

from constants import LOG_FILE_ENROLLMENT

logging.basicConfig(filename=LOG_FILE_ENROLLMENT, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# logging.basicConfig(filename='104_enrollment.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

num_threads = 20

def assign_value_if_not_null(value):
    if value is not None and value != "null":
        return value
    else:
        return ""

def create_enrollment_for_row(row):
    BeneficiaryID, MappingBenRegId, BeneficiaryRegID, CreatedDate, FirstName, MiddleName, LastName, Gender, DOB, VanID = row

    CreatedDate = CreatedDate.strftime("%Y-%m-%d")

    # org_unit_id, option_name = get_org_unit_and_option_data(PermSubDistrictId, PermVillageId)
    org_unit_id = get_org_unit_data(VanID)

    existing_tei = check_existing_tei(org_unit_id, MappingBenRegId)

    if existing_tei:
        print(f"TEI already exists for BeneficiaryRegID {MappingBenRegId}. orgUnit Id {org_unit_id} . Skipping.")
        logging.info(f"TEI already exists for BeneficiaryRegID {MappingBenRegId}.orgUnit Id {org_unit_id} . Skipping.")
        return

    enrollment_data = {
        "trackedEntityType": "T10dZwFVdkz",
        "orgUnit": org_unit_id,
        "attributes": [
            {"attribute": "pQLwsC8cu9R", "value": str(assign_value_if_not_null(BeneficiaryID))},
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
                "program": "hQUeRtU70wj",
                "enrollmentDate": CreatedDate,
                "incidentDate": CreatedDate
            }
        ]
    }
    response = create_enrollment(enrollment_data, org_unit_id,CreatedDate)
    #print(f"enrollment_response {response} " )

    if response.status_code == 200:
        logging.info(f"Enrollment created successfully for BeneficiaryRegID {MappingBenRegId} . orgUnit Id : {org_unit_id}")
        print(f"Enrollment created successfully for BeneficiaryRegID {MappingBenRegId}", f"orgUnit Id : {org_unit_id}")
    else:
        logging.error(f"Failed to create enrollment for BeneficiaryRegID {MappingBenRegId}. orgUnit Id : {org_unit_id} . Status code: {response.status_code} . error details: {response.json()}")

try:
    mysql_connection = connect_to_mysql()

    if mysql_connection.is_connected():
        logging.info("bayer TM enrollment query")
        print("bayer TM db enrollment query")
        print("Connected to MySQL database")
        logging.info("Connected to MySQL database")
        mysql_cursor = mysql_connection.cursor()
        mysql_query = f"""

        SELECT mb.BeneficiaryID, i_ben_mapping.BenRegId AS MappingBenRegId, i_ben_details.BeneficiaryRegID, 
        CAST(i_ben_mapping.CreatedDate AS DATE) AS CreatedDate, i_ben_details.FirstName,
        i_ben_details.MiddleName, i_ben_details.LastName, i_ben_details.Gender,
        IF(i_ben_details.DOB IS NOT NULL, DATE_FORMAT(i_ben_details.DOB, '%Y-01-01'), NULL) AS DOB,
        bayerVan.VanID 
        
        FROM db_identity.i_beneficiarymapping i_ben_mapping

        INNER join db_identity.m_beneficiaryregidmapping_vtbl mb on mb.BenRegId=i_ben_mapping.BenRegId

        INNER JOIN db_identity.i_beneficiarydetails_vtbl i_ben_details ON 
        i_ben_details.BeneficiaryDetailsId = i_ben_mapping.BenDetailsId

        INNER JOIN db_iemr.m_van bayerVan ON  bayerVan.VanID = db_identity.i_ben_mapping.VanID

        WHERE i_ben_mapping.BenRegId IS NOT NULL AND bayerVan.ProviderServiceMapID = 1
        AND i_ben_mapping.CreatedDate between '2022-01-01 00:00:00' and '2024-12-31 23:59:59'
        ORDER by MappingBenRegId ASC;

        """
        mysql_cursor.execute(mysql_query)
        mysql_rows = mysql_cursor.fetchall()
        logging.info(f"mysql_rows size {len(mysql_rows)}")
        print(f"mysql_rows size {len(mysql_rows)}")
        for row in mysql_rows:
            #print(f"mysql_rows {row}")
            create_enrollment_for_row(row)


        #with ThreadPoolExecutor(max_workers=num_threads) as executor:
            #for row in mysql_rows:
                #executor.submit(create_enrollment_for_row, row)

except Exception as e:
    logging.error(f"Error: {str(e)}")
    print(f"Error: {str(e)}")
finally:
    if 'mysql_cursor' in locals():
        mysql_cursor.close()
    if 'mysql_connection' in locals() and mysql_connection.is_connected():
        mysql_connection.close()
        logging.info("MySQL connection closed")
