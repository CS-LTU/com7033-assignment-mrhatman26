import mysql.connector
import hashlib
from db_config import db_config

'''Misc Commands'''
def string_hash(text):
    text = text.encode('utf-8')
    hash = hashlib.sha256()
    hash.update(text)
    return hash.hexdigest()

'''User Commands'''
#Check
def user_check_exists(username):
    database = mysql.connector.connect(**db_config)
    cursor = database.cursor()
    cursor.execute("SELECT user_id FROM table_users WHERE user_fullname = %s", (str(username),))
    if len(cursor.fetchall()) > 0:
        cursor.close()
        database.close()
        return True
    else:
        cursor.close()
        database.close()
        return False
    
def user_check_reconfirm(user_id):
    user = []
    database = mysql.connector.connect(**db_config)
    cursor = database.cursor()
    cursor.execute("SELECT user_id, user_fullname FROM table_users WHERE user_id = %s", (str(user_id),))
    for item in cursor.fetchall():
        user.append(item[0])
        user.append(item[1])
    cursor.close()
    database.close()
    return user

def user_check_validate(userdata):
    if user_check_exists(userdata["username"]):
        database = mysql.connector.connect(**db_config)
        cursor = database.cursor()
        cursor.execute("SELECT user_password FROM table_users WHERE user_name = %s", (str(userdata[""]),))
        if string_hash(userdata["password"]) == cursor.fetchall()[0][0]:
            cursor.close()
            database.close()
            return True
        else:
            return False
    else:
        return False
    
#Get
def user_get_amount():
    database = mysql.connector.connect(**db_config)
    cursor = database.cursor()
    cursor.execute("SELECT user_id FROM table_users")
    user_amount = len(cursor.fetchall())
    cursor.close()
    database.close()
    return user_amount

def user_get_id(username):
    user_id = None
    database = mysql.connector.connect(**db_config)
    cursor = database.cursor()
    cursor.execute("SELECT user_id FROM table_users WHERE user_fullname = %s", (str(username),))
    ids = cursor.fetchall()
    if len(ids) > 0:
        user_id = cursor.fetchall()[0][0]
    cursor.close()
    database.close()
    return user_id
                   
def user_get_all():
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

'''Patient commands'''
def insert_patients_data(patient_data):
    pass
