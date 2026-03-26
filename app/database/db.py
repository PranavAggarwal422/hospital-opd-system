import mysql.connector 
from flask import current_app 

def get_db_connection() : 
    try : 
        connection = mysql.connector.connect(
            host = current_app.config["MYSQL_HOST"], 
            user = current_app.config["MYSQL_USER"], 
            password = current_app.config["MYSQL_PASSWORD"], 
            database = current_app.config["MYSQL_DB"],
            port= current_app.config["MYSQL_PORT"]
        )
        return connection 
    
    except mysql.connector.Error as err : 
        raise err 