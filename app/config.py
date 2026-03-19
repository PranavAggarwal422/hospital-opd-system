import os 

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    # UPLOAD_FOLDER = os.path.join(BASE_DIR, "..", "uploads")
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")

    MYSQL_HOST = os.environ.get("MYSQL_HOST")
    MYSQL_USER = os.environ.get("MYSQL_USER")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD")
    MYSQL_DB = os.environ.get("MYSQL_DB")