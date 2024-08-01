#import mysql_connection
#import dhis2_integration
import dhis2_api_interaction
import database_connection
import logging, datetime
import pandas as pd
from datetime import date, timedelta,datetime
from database_connection import connect_to_mysql

# MySQL connection parameters
#mysql_host = '192.168.20.7'
#mysql_port = 3306
#mysql_database = 'db_iemr'
#mysql_user = 'db_amrit_dhis2'
#mysql_password = 'Dhis_DB@2024$'

# DHIS2 API parameters
dhis2_base_url = '####'
dhis2_username = '####'
dhis2_password = '####'

from constants import LOG_FILE_EVENT

logging.basicConfig(filename=LOG_FILE_EVENT, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# logging.basicConfig(filename='bayer_event.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

mysql_connection = connect_to_mysql()
#mysql_conn = database_connection.establish_mysql_connection(mysql_host, mysql_port, mysql_user, mysql_password, mysql_database)

# logging.info("MySQL connection closed")
print("Connected to MySQL database")
logging.info("Connected to MySQL database")

current_time_start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print( f" pushing event start . { current_time_start }" )
logging.info(f" pushing event start . { current_time_start }")
cursor = mysql_connection.cursor()

logging.info("JHarkhand MMU Event query")
current_time_start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print( f" pushing event start . { current_time_start }" )
logging.info(f" pushing Enrollment start . { current_time_start }")
# Returns the current local date
today = date.today()
todayStartDate = today.strftime("%Y-%m-%d") + " " + "00:00:00"
oneDayBeforeToday = today - timedelta(days=1)
oneDayBeforeTodayStartDate = oneDayBeforeToday.strftime("%Y-%m-%d") + " " + "00:00:00"
oneDayBeforeTodayEndDate = oneDayBeforeToday.strftime("%Y-%m-%d") + " " + "23:59:59"
todayEndDate = today.strftime("%Y-%m-%d") + " " + "23:59:59"
print(f"oneDayBeforeTodayStartDate {oneDayBeforeTodayStartDate}", f"todayEnd : {todayEndDate}")
logging.info(f"oneDayBeforeTodayStartDate {oneDayBeforeTodayStartDate}. todayEnd : {todayEndDate}")

results = database_connection.fetch_mysql_data(cursor, oneDayBeforeTodayStartDate, todayEndDate)

print(f"mysql_events Query size {len(results)}")
logging.info(f"mysql_events Query size {len(results)}")

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
    #print(f"mysql_rows {result}")
    Visitcode,BenVisitID,BeneficiaryRegID,VisitNo,CreatedDate,vanid,AgeOnVisit,VisitReason,VisitCategory,PregnancyStatus,Referal_Visitcode,referredToInstituteName,referralreason,ProvisionalDiagnosis,phyanthropometry_bmi,nurse_rbs,Weight_Kg,Height_cm,WaistCircumference_cm,Temperature,SystolicBP_1stReading,DiastolicBP_1stReading,ComorbidCondition_Fulltext,Comobrid_Diabetes,Comobrid_Hypertension,Comobrid_Asthma,Comobrid_Epilepsy,Comobrid_Heart_Disease,Comobrid_Kidney_Disease,Comobrid_Sickle_cell,Labtest_Prescribed,Drug_Prescribedcode,Drug_Dispensecode,diagnosisprovided_full_text,DiagnosisProvided1,NCD_Condition,ncd_condition_full_text,PulseRate,spo2,feto_Visitcode,TestName,GenericDrugName,Labtest_Done_Visitcode,Total_lab_test,Random_Blood_Sugar,Hemoglobin,UrineAlbumin,UrineSugar,Urine_Pregnancy_test,Malaria,ECG,HbA1c,Liver_Function_Test,Liverfunctiontest_Direct_Bilirubin,Liverfunctiontest_SGPT,Liverfunctiontest_SGOT,Liverfunctiontest_Total_Serum_Bilirubin,Liverfunctiontest_Blood_Urea,Liverfunctiontest_Serum_Creatinine,Renal_function_test,Renalfunctiontest_Serum_Creatinine,Renalfunctiontest_Blood_Urea,Lipid_profile,Lipidprofile_Serum_Total_Cholesterol,Lipidprofile_Serum_HDL,Lipidprofile_LDL,Lipidprofile_Serum_Triglycerides,Post_Lunch_Blood_Sugar,Fasting_Blood_Sugar,Complete_Blood_Picture,CBP_ESR,CBP_Monocytes,CBP_Hemoglobin,CBP_RBC,CBP_Lymphocytes,CBP_Neutrophils,CBP_Basophils,CBP_Eosinophils,CBP_MCV,CBP_MCH,CBP_MCHC,CBP_Hematocrit,CBP_Platelet_Count,CBP_Total_Leucocyte_Count,Widal_Test,Sputum_AFB_Test,Sickle_Cell_Disease_Test,HBsAg,Complete_Urine_Examination,Complete_Urine_Examination_Total_Leucocyte_Count,Complete_Urine_Examination_Urine_for_Nitrite,Chikungunya,Hb_Electrophoresis,Dengue_NS1_Antigen,Dengue_Antibody_Test,HIV1_HIV2_RDT,Visual_Acuity_Test,Blood_Group,VDRL_Test,Syphilis,Serum_Uric_Acid,Serum_Total_Cholesterol,Hepatitis_B,Hepatitis_C,ESR,RBS_Status = result

    #CreatedDate = CreatedDate.strftime("%Y-%m-%d")
    
    org_unit_id = dhis2_api_interaction.get_org_unit_data(vanid)
    tei_data = dhis2_api_interaction.get_tei_data(BeneficiaryRegID, tei_data_cache)

    if tei_data:
        #print(f"TEI found for BeneficiaryRegID: {BeneficiaryRegID}. tei_data : {tei_data}" )
        event_payload = dhis2_api_interaction.construct_sql_query_event_payload(
            tei_data,Visitcode,BenVisitID,BeneficiaryRegID,VisitNo,CreatedDate,
            vanid,AgeOnVisit,VisitReason,VisitCategory,PregnancyStatus,Referal_Visitcode,
            referredToInstituteName,referralreason,ProvisionalDiagnosis,phyanthropometry_bmi,
            nurse_rbs,Weight_Kg,Height_cm,WaistCircumference_cm,Temperature,SystolicBP_1stReading,
            DiastolicBP_1stReading,ComorbidCondition_Fulltext,Comobrid_Diabetes,Comobrid_Hypertension,
            Comobrid_Asthma,Comobrid_Epilepsy,Comobrid_Heart_Disease,Comobrid_Kidney_Disease,
            Comobrid_Sickle_cell,Labtest_Prescribed,Drug_Prescribedcode,Drug_Dispensecode,
            diagnosisprovided_full_text,DiagnosisProvided1,NCD_Condition,ncd_condition_full_text,
            PulseRate,spo2,feto_Visitcode,TestName,GenericDrugName,Labtest_Done_Visitcode,
            Total_lab_test,Random_Blood_Sugar,Hemoglobin,UrineAlbumin,UrineSugar,Urine_Pregnancy_test,
            Malaria,ECG,HbA1c,Liver_Function_Test,Liverfunctiontest_Direct_Bilirubin,Liverfunctiontest_SGPT,
            Liverfunctiontest_SGOT,Liverfunctiontest_Total_Serum_Bilirubin,Liverfunctiontest_Blood_Urea,
            Liverfunctiontest_Serum_Creatinine,Renal_function_test,Renalfunctiontest_Serum_Creatinine,
            Renalfunctiontest_Blood_Urea,Lipid_profile,Lipidprofile_Serum_Total_Cholesterol,Lipidprofile_Serum_HDL,
            Lipidprofile_LDL,Lipidprofile_Serum_Triglycerides,Post_Lunch_Blood_Sugar,Fasting_Blood_Sugar,
            Complete_Blood_Picture,CBP_ESR,CBP_Monocytes,CBP_Hemoglobin,CBP_RBC,CBP_Lymphocytes,CBP_Neutrophils,
            CBP_Basophils,CBP_Eosinophils,CBP_MCV,CBP_MCH,CBP_MCHC,CBP_Hematocrit,CBP_Platelet_Count,CBP_Total_Leucocyte_Count,Widal_Test,
            Sputum_AFB_Test,Sickle_Cell_Disease_Test,HBsAg,Complete_Urine_Examination,Complete_Urine_Examination_Total_Leucocyte_Count,
            Complete_Urine_Examination_Urine_for_Nitrite,Chikungunya,Hb_Electrophoresis,Dengue_NS1_Antigen,
            Dengue_Antibody_Test,HIV1_HIV2_RDT,Visual_Acuity_Test,Blood_Group,VDRL_Test,Syphilis,Serum_Uric_Acid,
            Serum_Total_Cholesterol,Hepatitis_B,Hepatitis_C,ESR,RBS_Status)
        
        dhis2_api_interaction.create_events_in_dhis2( event_payload,BeneficiaryRegID, Visitcode )

        
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
    #dhis2_api_interaction.create_events_in_dhis2( event_payload,BeneficiaryRegID, Visitcode )

current_time_end = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print( f" pushing event finished . { current_time_end }" )
logging.info(f" pushing event finished . { current_time_end }")