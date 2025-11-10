import mysql.connector
import os


def get_db():
    return mysql.connector.connect(
        host=os.getenv("GYM_DB_SERVER"),
        user=os.getenv("GYM_DB_USERNAME"),
        password=os.getenv("GYM_DB_PASSWORD"),
        database=os.getenv("GYM_DB_NAME")
    )
