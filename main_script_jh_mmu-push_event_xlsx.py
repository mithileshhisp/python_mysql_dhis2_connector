#import mysql_connection
#import dhis2_integration
from dhis2_api_interaction import get_org_unit_data, get_tei_data, construct_xlsx_event_payload, create_events_in_dhis2, construct_xlsx_event_payload,create_events_in_dhis2_xlsx
import database_connection
import logging, datetime
import pandas as pd
from database_connection import connect_to_mysql


from constants import LOG_FILE_EVENT

logging.basicConfig(filename=LOG_FILE_EVENT, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# logging.basicConfig(filename='bayer_event.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

#mysql_connection = connect_to_mysql()
#mysql_conn = database_connection.establish_mysql_connection(mysql_host, mysql_port, mysql_user, mysql_password, mysql_database)

# logging.info("MySQL connection closed")

#print("Connected to MySQL database")
#logging.info("Connected to MySQL database")
#cursor = mysql_connection.cursor()

#results = database_connection.fetch_mysql_data(cursor)

#mysql_connection.close()

# Get the current date and time
current_time_start = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print( f" pushing event start . { current_time_start }" )
logging.info(f" pushing event start . { current_time_start }")

tei_data_cache = {}
events_by_reg_id = {}


#excel_path = 'hwc_event_data.xlsx' 
#data_dict = read_excel_to_dict(excel_path)
'''
import pandas as pd
file_path = 'read_sample.xlsx'
data = pd.read_excel(file_path)
columns_of_interest = ['Column1', 'Column2', 'Column3', 'Column4']
data_of_interest = data[columns_of_interest]
for index, row in data_of_interest.iterrows():
    print(f"Row {index + 1}:")
    for col in columns_of_interest:
        print(f"  {col}: {row[col]}")
    print()
'''


excel_file_path = 'JHarkhand July_missing_event.xlsx'
data = pd.read_excel(excel_file_path)
'''
columns_of_interest = ['event', 'orgUnit', 'trackedEntityInstance', BeneficiaryRegID, 'eventDate','BenVisitID',
                       'VisitNo', 'AgeOnVisit', 'VisitReason', 'VisitCategory','ProvisionalDiagnosis',
                       'phyanthropometry_bmi', 'nurse_rbs','SystolicBP_1stReading','DiastolicBP_1stReading',
                       'PrescriptionID', 'ProcedureID', 'ProcedureName', 'TestResultValue']
'''                       
#data_of_interest = data[columns_of_interest]
for index, row in data.iterrows():
    #print(f"Row {index + 1}: {row}" )
    
    #row['event'],row['orgUnit'],row['trackedEntityInstance'],
    event_payload = construct_xlsx_event_payload(row['trackedEntityInstance'],row['orgUnit'],row['Visitcode'],row['BenVisitID'],row['BeneficiaryRegID'],row['VisitNo'],
                                                 row['CreatedDate'],row['vanid'],row['AgeOnVisit'],row['VisitReason'],
                                                 row['VisitCategory'],row['PregnancyStatus'],row['Referal_Visitcode'],
                                                 row['referredToInstituteName'],row['referralreason'],
                                                 row['ProvisionalDiagnosis'],row['phyanthropometry_bmi'], row['nurse_rbs'],
                                                 row['Weight_Kg'],row['Height_cm'],row['WaistCircumference_cm'],row['Temperature'],
                                                 row['SystolicBP_1stReading'],row['DiastolicBP_1stReading'],row['ComorbidCondition_Fulltext'],
                                                 row['Comobrid_Diabetes'],row['Comobrid_Hypertension'],row['Comobrid_Asthma'],
                                                 row['Comobrid_Epilepsy'],row['Comobrid_Heart_Disease'],row['Comobrid_Kidney_Disease'],row['Comobrid_Sickle_cell'],
                                                 row['Labtest_Prescribed'],row['Drug_Prescribedcode'],row['Drug_Dispensecode'],row['diagnosisprovided_full_text'],
                                                 row['DiagnosisProvided1'],row['NCD_Condition'],row['ncd_condition_full_text'],row['PulseRate'], row['spo2'],row['feto_Visitcode'],
                                                 row['TestName'],row['GenericDrugName'],row['Labtest_Done_Visitcode'],row['Total_lab_test'],row['Random_Blood_Sugar'],
                                                 row['Hemoglobin'],row['UrineAlbumin'],row['UrineSugar'],row['Urine_Pregnancy_test'],row['Malaria'],
                                                 row['ECG'], row['HbA1c'],row['Liver_Function_Test'], row['Liverfunctiontest_Direct_Bilirubin'],
                                                 row['Liverfunctiontest_SGPT'], row['Liverfunctiontest_SGOT'],row['Liverfunctiontest_Total_Serum_Bilirubin'], 
                                                 row['Liverfunctiontest_Blood_Urea'], row['Liverfunctiontest_Serum_Creatinine'],
                                                 row['Renal_function_test'], row['Renalfunctiontest_Serum_Creatinine'], row['Renalfunctiontest_Blood_Urea'],                                               
                                                 row['Lipid_profile'],row['Lipidprofile_Serum_Total_Cholesterol'],row['Lipidprofile_Serum_HDL'],row['Lipidprofile_LDL'],row['Lipidprofile_Serum_Triglycerides'],
                                                 row['Post_Lunch_Blood_Sugar'], row['Fasting_Blood_Sugar'], row['Complete_Blood_Picture'],                                               
                                                 row['CBP_ESR'],row['CBP_Monocytes'],row['CBP_Hemoglobin'],row['CBP_RBC'],row['CBP_Lymphocytes'],
                                                 row['CBP_Neutrophils'],row['CBP_Basophils'],row['CBP_Eosinophils'],row['CBP_MCV'],row['CBP_MCH'],
                                                 row['CBP_MCHC'],row['CBP_Hematocrit'],row['CBP_Platelet_Count'],row['CBP_Total_Leucocyte_Count'],row['Widal_Test'],                                                 
                                                 row['Sputum_AFB_Test'], row['Sickle_Cell_Disease_Test'], row['HBsAg'],                                               
                                                 row['Complete_Urine_Examination'],row['Complete_Urine_Examination_Total_Leucocyte_Count'],
                                                 row['Complete_Urine_Examination_Urine_for_Nitrite'],row['Chikungunya'],row['Hb_Electrophoresis'],
                                                 row['Dengue_NS1_Antigen'],row['Dengue_Antibody_Test'],row['HIV1_HIV2_RDT'],row['Visual_Acuity_Test'],
                                                 row['Blood_Group'],row['VDRL_Test'],row['Syphilis'],row['Serum_Uric_Acid'],
                                                 row['Serum_Total_Cholesterol'],row['Hepatitis_B'], row['Hepatitis_C'], row['ESR'], row['RBS_Status'])

    #print(f" Row {index + 2} .. {row['BeneficiaryRegID']}  ")

    #print( f" event_payload size . { len(event_payload) }" )

    #logging.info(f" Row {index + 2} .. {row['BeneficiaryRegID']}  ")
    #logging.info(f" pushing event BeneficiaryRegID . {row['BeneficiaryRegID']} ")
    #for col in columns_of_interest:
        #print(f"  {col}: {row[col]}")
    
    create_events_in_dhis2_xlsx( event_payload, row['BeneficiaryRegID'], row['Visitcode'], index + 2 )


current_time_end = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print( f" pushing event finished . { current_time_end }" )
logging.info(f" pushing event finished . { current_time_end }")

'''
for result in results:
    BenVisitID, BeneficiaryRegID, VisitNo, CreatedDate, VanID, AgeOnVisit, VisitReason, VisitCategory, RCHID, ProvisionalDiagnosis, SystolicBP_1stReading, DiastolicBP_1stReading, Status, referredToInstituteName, ProcedureName, NCD_Condition1, NCD_Condition2, NCD_Condition3, NCD_Condition4, DiagnosisProvided1, DiagnosisProvided2, DiagnosisProvided3, DiagnosisProvided4, DiagnosisProvided5 = result

    CreatedDate = CreatedDate.strftime("%Y-%m-%d")
    
    org_unit_id = get_org_unit_data(VanID)

    tei_data = get_tei_data(org_unit_id, BeneficiaryRegID, tei_data_cache)

    if tei_data:
        event_payload = construct_xlsx_event_payload(tei_data, CreatedDate,
            BenVisitID, BeneficiaryRegID, VisitNo, AgeOnVisit, 
            VisitReason, VisitCategory, RCHID, ProvisionalDiagnosis, 
            SystolicBP_1stReading, DiastolicBP_1stReading, Status, 
            referredToInstituteName, ProcedureName, NCD_Condition1, NCD_Condition2, 
            NCD_Condition3, NCD_Condition4, DiagnosisProvided1, DiagnosisProvided2, 
            DiagnosisProvided3, DiagnosisProvided4, DiagnosisProvided5 )

    create_events_in_dhis2( event_payload,BeneficiaryRegID, BenVisitID )
    '''
