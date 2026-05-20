import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DB"),
            port=int(os.getenv("MYSQL_PORT"))
        )
        return connection

    except mysql.connector.Error as err:
        raise err
    