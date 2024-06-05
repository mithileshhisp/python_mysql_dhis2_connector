# database_connection.py
# Author: mithilesh
import mysql.connector
import logging
#mysql_host = ''
#mysql_port = 1234
#mysql_database = '###'
#mysql_user = '#####'
#mysql_password = '######'

# MySQL connection parameters
mysql_host = '*****'
mysql_port = 1234
mysql_database = '*****'
mysql_user = '****'
mysql_password = '*****'


def connect_to_mysql():
    return mysql.connector.connect(
        host=mysql_host,
        port=mysql_port,
        database=mysql_database,
        user=mysql_user,
        password=mysql_password
    )

def establish_mysql_connection(mysql_host, mysql_port, mysql_user, mysql_password, mysql_database):
    mysql_conn = mysql.connector.connect(
        host=mysql_host,
        port=mysql_port,
        user=mysql_user,
        password=mysql_password,
        database=mysql_database
    )
    return mysql_conn


def fetch_mysql_data(cursor):
    # bayer TM event query hQUeRtU70wj
    logging.info("bayer TM EVENT query")
    print("bayer TM db EVENT query")
    print("Connected to MySQL database")
    logging.info("Connected to MySQL database")
        
    query = """

    SELECT db_iemr.t_benvisitdetail.BenVisitID, db_iemr.t_benvisitdetail.BeneficiaryRegID,
    db_iemr.t_benvisitdetail.VisitNo,
    CAST(db_iemr.t_benvisitdetail.CreatedDate AS DATE) AS CreatedDate, db_iemr.t_benvisitdetail.VanID,
    year(db_iemr.t_benvisitdetail.CreatedDate) - 
    year(IF(i_ben_details.DOB IS NOT NULL, DATE_FORMAT(i_ben_details.DOB, '%Y-01-01'), NULL)) as AgeOnVisit,

    db_iemr.t_benvisitdetail.VisitReason, db_iemr.t_benvisitdetail.VisitCategory,

    db_iemr.t_benvisitdetail.RCHID, pnc.ProvisionalDiagnosis, phy.SystolicBP_1stReading, phy.DiastolicBP_1stReading,
    tm.Status, referal.referredToInstituteName,testorder.ProcedureName,

    SUBSTRING_INDEX(SUBSTRING_INDEX(ncd.ncd_condition, '||', 1), '||', - 1) AS NCD_Condition1,
    CASE
        WHEN STRCMP(SUBSTRING_INDEX(SUBSTRING_INDEX(ncd.ncd_condition, '||', 1), '||', - 1), SUBSTRING_INDEX(SUBSTRING_INDEX(ncd.ncd_condition, '||', 2), '||', - 1)) <> 0 THEN SUBSTRING_INDEX(SUBSTRING_INDEX(ncd.ncd_condition, '||', 2), '||', - 1)
    END AS NCD_Condition2,
    CASE
        WHEN STRCMP(SUBSTRING_INDEX(SUBSTRING_INDEX(ncd.ncd_condition, '||', 2), '||', - 1), SUBSTRING_INDEX(SUBSTRING_INDEX(ncd.ncd_condition, '||', 3), '||', - 1)) <> 0 THEN SUBSTRING_INDEX(SUBSTRING_INDEX(ncd.ncd_condition, '||', 3), '||', - 1)
    END AS NCD_Condition3,
    CASE
        WHEN STRCMP(SUBSTRING_INDEX(SUBSTRING_INDEX(ncd.ncd_condition, '||', 3), '||', - 1), SUBSTRING_INDEX(SUBSTRING_INDEX(ncd.ncd_condition, '||', 4), '||', - 1)) <> 0 THEN SUBSTRING_INDEX(SUBSTRING_INDEX(ncd.ncd_condition, '||', 4), '||', - 1)
    END AS NCD_Condition4,
    
    SUBSTRING_INDEX(SUBSTRING_INDEX(DiagnosisProvided, '||', 1), '||', - 1) AS DiagnosisProvided1,
    CASE
        WHEN STRCMP(SUBSTRING_INDEX(SUBSTRING_INDEX(DiagnosisProvided, '||', 1), '||', - 1), SUBSTRING_INDEX(SUBSTRING_INDEX(DiagnosisProvided, '||', 2), '||', - 1)) <> 0 THEN SUBSTRING_INDEX(SUBSTRING_INDEX(DiagnosisProvided, '||', 2), '||', - 1)
    END AS DiagnosisProvided2,
    CASE
        WHEN STRCMP(SUBSTRING_INDEX(SUBSTRING_INDEX(DiagnosisProvided, '||', 2), '||', - 1), SUBSTRING_INDEX(SUBSTRING_INDEX(DiagnosisProvided, '||', 3), '||', - 1)) <> 0 THEN SUBSTRING_INDEX(SUBSTRING_INDEX(DiagnosisProvided, '||', 3), '||', - 1)
    END AS DiagnosisProvided3,
    CASE
        WHEN STRCMP(SUBSTRING_INDEX(SUBSTRING_INDEX(DiagnosisProvided, '||', 3), '||', - 1), SUBSTRING_INDEX(SUBSTRING_INDEX(DiagnosisProvided, '||', 4), '||', - 1)) <> 0 THEN SUBSTRING_INDEX(SUBSTRING_INDEX(DiagnosisProvided, '||', 4), '||', - 1)
    END AS DiagnosisProvided4,
    CASE
        WHEN STRCMP(SUBSTRING_INDEX(SUBSTRING_INDEX(DiagnosisProvided, '||', 4), '||', - 1), SUBSTRING_INDEX(SUBSTRING_INDEX(DiagnosisProvided, '||', 5), '||', - 1)) <> 0 THEN SUBSTRING_INDEX(SUBSTRING_INDEX(DiagnosisProvided, '||', 5), '||', - 1)
    END AS DiagnosisProvided5

    FROM db_iemr.t_benvisitdetail

    LEFT JOIN  db_identity.i_beneficiarymapping i_ben_mapping ON 
    i_ben_mapping.BenRegId = db_iemr.t_benvisitdetail.BeneficiaryRegID

    LEFT JOIN  db_identity.i_beneficiarydetails_vtbl i_ben_details ON 
    i_ben_details.BeneficiaryDetailsId = i_ben_mapping.BenDetailsId

    LEFT JOIN db_iemr.t_ancdiagnosis anc on anc.BenVisitID=db_iemr.t_benvisitdetail.BenVisitID
    LEFT JOIN db_iemr.t_pncdiagnosis pnc on pnc.BenVisitID=db_iemr.t_benvisitdetail.BenVisitID
    LEFT JOIN db_iemr.t_ncddiagnosis ncd on ncd.BenVisitID=db_iemr.t_benvisitdetail.BenVisitID
    LEFT JOIN db_iemr.t_phy_vitals phy on phy.BenVisitID=db_iemr.t_benvisitdetail.BenVisitID
    LEFT JOIN db_iemr.t_tmrequest tm on tm.BenVisitID=db_iemr.t_benvisitdetail.BenVisitID
    
    LEFT JOIN db_iemr.t_benreferdetails referal ON referal.BenVisitID=db_iemr.t_benvisitdetail.BenVisitID
    LEFT JOIN db_iemr.t_lab_testorder testorder ON testorder.BenVisitID=db_iemr.t_benvisitdetail.BenVisitID
    LEFT JOIN db_iemr.t_prescription prescription ON prescription.BenVisitID=db_iemr.t_benvisitdetail.BenVisitID

    WHERE i_ben_mapping.VanID  IN 
    ( SELECT VanID FROM db_iemr.m_van WHERE ProviderServiceMapID in (1));

    """
    cursor.execute(query)
    results = cursor.fetchall()
    logging.info(f"mysql_rows size {len(results)}")
    print(f"mysql_rows size {len(results)}")
    return results
