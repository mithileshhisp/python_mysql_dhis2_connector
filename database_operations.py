import mysql.connector
from mysql_config import *

def connect_to_mysql():
    return mysql.connector.connect(
        host=mysql_host,
        port=mysql_port,
        database=mysql_database,
        user=mysql_user,
        password=mysql_password
    )

def connect_to_mysql2():
    return mysql.connector.connect(
        host=mysql_host,
        port=mysql_port,
        database=mysql_database2,
        user=mysql_user,
        password=mysql_password
    )

def execute_mysql_query(mysql_connection, query):
    cursor = mysql_connection.cursor()
    cursor.execute(query)
    return cursor.fetchall()

def close_mysql_connection(mysql_connection):
    if mysql_connection.is_connected():
        mysql_connection.close()
