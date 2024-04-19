import mysql.connector

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
    query = """
    SELECT DISTINCT ####;
    """
    cursor.execute(query)
    results = cursor.fetchall()
    return results
