import mysql.connector
from db_config import db_config

'''GET Commands'''
#Users
def get_users():
    user_list = []
    database = mysql.connector.connect(**db_config)
    cursor = database.cursor()
    cursor.execute("SELECT user_id, user_fullname, user_email, user_phone FROM table_users")
    for user_data in cursor.fetchall():
        user_list.append({
            "user_id": user_data[0],
            "user_fullname": user_data[1],
            "user_email": user_datap[2],
            "user_phone": user_data[3]
        })
    cursor.close()
    database.close()
    return user_list

'''INSERT commands'''
def insert_patients_data():
    pass
