import mysql.connector
import hashlib
from db_config import get_db_config

deployed = False

'''Misc Commands'''
def string_hash(text):
    text = text.encode('utf-8')
    hash = hashlib.sha256()
    hash.update(text)
    return hash.hexdigest()

def str_to_bool(YesNo):
    if YesNo.upper() == "YES":
        return True
    else:
        return False
    

'''User Commands'''
#Check
def user_check_exists(username):
    database = mysql.connector.connect(**get_db_config(deployed))
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
    database = mysql.connector.connect(**get_db_config(deployed))
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
        database = mysql.connector.connect(**get_db_config(deployed))
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
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    cursor.execute("SELECT user_id FROM table_users")
    user_amount = len(cursor.fetchall())
    cursor.close()
    database.close()
    return user_amount

def user_get_last_id():
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    cursor.execute("SELECT user_id FROM table_users")
    last_id = cursor.fetchall()
    if len(last_id) >= 1:
        last_id = last_id[-1][0] + 1
    else:
        last_id = 0
    cursor.close()
    database.close()
    return last_id

def user_get_id(username):
    user_id = None
    database = mysql.connector.connect(**get_db_config(deployed))
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
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    cursor.execute("SELECT user_id, user_fullname, user_email, user_phone FROM table_users")
    for user_data in cursor.fetchall():
        user_list.append({
            "user_id": user_data[0],
            "user_fullname": user_data[1],
            "user_email": user_data[2],
            "user_phone": user_data[3]
        })
    cursor.close()
    database.close()
    return user_list

#Insert
def user_create(userdata):
    if user_check_exists(userdata["email"]):
        return False
    else:
        userdata["password"] = string_hash(userdata["password"])
        userdata["id"] = user_get_last_id()
        database = mysql.connector.connect(**get_db_config(deployed))
        cursor = database.cursor()
        print(userdata)
        cursor.execute("INSERT INTO table_users VALUES(%s, %s, %s, %s, %s, %s)", (userdata["id"], str(userdata["fullname"]), userdata["password"], str(userdata["email"]), str(userdata["phone"]), 0))
        database.commit()
        cursor.close()
        database.close()
        return True

'''Patient commands'''
def insert_patients_data(patient_data):
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    cursor.execute("SELECT patient_id FROM table_patient_data")
    fetch = cursor.fetchall()
    if len(fetch) >= 1:
        new_id = int(fetch[-1][0]) + 1
    else:
        new_id = 0
    cursor.execute("INSERT INTO table_patient_data VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (str(new_id), str(patient_data["patient_gender"]), patient_data["patient_age"], str(patient_data["patient_hyperT"]), str(patient_data["patient_hDisease"]), str(patient_data["patient_married"]), str(patient_data["patient_work_type"]), str(patient_data["patient_residence_type"]), str(patient_data["patient_avg_gLevel"]), patient_data["patient_bmi"], str(patient_data["patient_smoked"]), str(patient_data["patient_stroke"]),))
    database.commit()
    cursor.close()
    database.close()
