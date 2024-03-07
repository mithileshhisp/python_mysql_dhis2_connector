import mysql.connector
import requests
host = '****'
port = ****
database = '****'
user = '****'
password = '****'
dhis2_api_url = "******"
dhis2_username = "****"
dhis2_password = "*****"
try:
    connection = mysql.connector.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password
    )
    if connection.is_connected():
        print("Connected to MySQL database")
        cursor = connection.cursor()
        query = "SELECT StateCode , GovtStateID  from m_state"
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            print(row)
except Exception as e:
    print(f"Error: {str(e)}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'connection' in locals() and connection.is_connected():
        connection.close()
        print("MySQL connection closed")