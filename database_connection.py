# database_connection.py
# Author: mithilesh
import mysql.connector

#mysql_host = ''
#mysql_port = 1234
#mysql_database = '###'
#mysql_user = '#####'
#mysql_password = '######'

# MySQL connection parameters
mysql_host = ''
mysql_port = 
mysql_database = ''
mysql_user = ''
mysql_password = ''


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
    # 104 event query vyQPQ07JB9M
    query = """

    SELECT distinct db_iemr.t_bencall.BenCallID,db_iemr.t_bencall.CallID, 
    db_iemr.t_bencall.BeneficiaryRegID, CAST(db_iemr.t_bencall.Calltime AS DATE) As CreatedDate,
    year(db_iemr.t_bencall.CreatedDate) -
    year(IF(i_ben_details.DOB IS NOT NULL, DATE_FORMAT(i_ben_details.DOB, '%Y-01-01'), NULL)) as AgeOnVisit,

    IF(db_iemr.t_bencall.is1097 = 1, 'true', 'false') AS Is1097,
    IF(db_iemr.t_bencall.IsOutbound = 1, 'true', 'false') AS IsOutbound,

    c.CategoryName, s.SubCategoryName, p.PrescriptionID, db_iemr.t_bencall.ReceivedRoleName,

    TIME_TO_SEC(TIMEDIFF(db_iemr.t_bencall.CallEndTime,db_iemr.t_bencall.CallTime)) AS CallDurationInSeconds,

    db_iemr.t_bencall.TypeOfComplaint, mct.CallType, mct.CallGroupType,
    b.SelecteDiagnosis As Diasease, b.DiseaseSummary As Algorithm

    FROM db_iemr.t_bencall

    LEFT JOIN  db_identity.i_beneficiarymapping i_ben_mapping ON
    i_ben_mapping.BenRegId = db_iemr.t_bencall.BeneficiaryRegID

    LEFT JOIN  db_identity.i_beneficiarydetails i_ben_details ON
    i_ben_details.BeneficiaryDetailsId = i_ben_mapping.BenDetailsId

    left join db_iemr.t_104benmedhistory b on b.BenCallID = db_iemr.t_bencall.BenCallID
    left join db_iemr.t_104prescription p on p.BenCallID=b.BenCallID
    inner join db_iemr.m_calltype mct on mct.CallTypeID=db_iemr.t_bencall.CallTypeID
    left join db_iemr.m_category c on c.CategoryID=b.CategoryID
    left join db_iemr.m_subcategory s on s.SubCategoryID=b.SubCategoryID

    WHERE db_iemr.t_bencall.BeneficiaryRegID IS NOT NULL
    AND db_iemr.t_bencall.Calltime order by BeneficiaryRegID
    between '2024-01-01 00:00:00' and '2024-03-31 23:59:59' 
    ORDER BY BeneficiaryRegID ASC;

    """
    cursor.execute(query)
    results = cursor.fetchall()
    return results
