from os import stat
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
    cursor.execute("SELECT user_id FROM table_users WHERE user_email = %s", (str(username),))
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
    cursor.execute("SELECT user_id, user_fullname, user_admin FROM table_users WHERE user_id = %s", (str(user_id),))
    for item in cursor.fetchall():
        user.append(item[0])
        user.append(item[1])
        user.append(item[2])
    cursor.close()
    database.close()
    return user

def user_check_validate(userdata):
    print(userdata)
    if user_check_exists(userdata["username"]):
        database = mysql.connector.connect(**get_db_config(deployed))
        cursor = database.cursor()
        cursor.execute("SELECT user_password FROM table_users WHERE user_email = %s", (str(userdata["username"]),))
        hashed_data = string_hash(userdata["password"])
        if hashed_data == cursor.fetchall()[0][0]:
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
    cursor.execute("SELECT user_id FROM table_users WHERE user_email = %s", (str(username),))
    ids = cursor.fetchall()
    if len(ids) > 0:
        user_id = ids[0][0]
    cursor.close()
    database.close()
    return user_id
                   
def user_get_all():
    user_list = []
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    cursor.execute("SELECT user_id, user_fullname, user_email, user_phone, user_admin FROM table_users")
    for user_data in cursor.fetchall():
        user_list.append({
            "user_id": user_data[0],
            "user_fullname": user_data[1],
            "user_email": user_data[2],
            "user_phone": user_data[3],
            "user_admin": user_data[4]
        })
    cursor.close()
    database.close()
    return user_list

def user_get_username(user_id):
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    cursor.execute("SELECT user_email FROM table_users WHERE user_id = %s", (user_id,))
    try:
        fetch = cursor.fetchall()[0][0]
    except:
        fetch = "Unknown User"
    cursor.close()
    database.close()
    return fetch

def user_get_single(user_id):
    user_data = {}
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    cursor.execute("SELECT user_fullname, user_email, user_phone FROM table_users WHERE user_id = %s", (user_id,))
    for user_info in cursor.fetchall():
        user_data["user_fullname"] = user_info[0]
        user_data["user_email"] = user_info[1]
        user_data["user_phone"] = user_info[2]
    return user_data

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
    
#Update
def user_update(userdata):
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    if user_check_exists(userdata["email"]):
        cursor.execute("SELECT user_id FROM table_users WHERE user_email = %s", (str(userdata["email"]),))
        fetch = cursor.fetchall()
        if len(fetch) >= 1:
            if userdata["id"] != fetch[0][0]:
                return False
    old_userdata = user_get_single(userdata["id"])
    if userdata["fullname"] == "":
        userdata["fullname"] = old_userdata["user_fullname"]
    if userdata["email"] == "":
        userdata["email"] = old_userdata["user_email"]
    if userdata["phone"] == "":
        userdata["phone"] = old_userdata["user_phone"]
    if userdata["password"] == "":
        cursor.execute("UPDATE table_users SET user_fullname = %s, user_email = %s, user_phone = %s WHERE user_id = %s", (str(userdata["fullname"]), str(userdata["email"]), str(userdata["phone"]), str(userdata["id"]),))
    else:
        userdata["password"] = string_hash(userdata["password"])
        cursor.execute("UPDATE table_users SET user_fullname = %s, user_password = %s, user_email = %s, user_phone = %s WHERE user_id = %s", (str(userdata["fullname"]), str(userdata["password"]), str(userdata["email"]), str(userdata["phone"]), str(userdata["id"]),))
    database.commit()
    cursor.close()
    database.close()
    return True

'''Patient commands'''
#Insert
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
    return new_id

def insert_new_patient(subdata, userid):
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    cursor.execute("SELECT patient_id FROM table_patient_data")
    fetch = cursor.fetchall()
    if len(fetch) >= 1:
        new_id = int(fetch[-1][0]) + 1
    else:
        new_id = 0
    cursor.execute("INSERT INTO table_patient_data VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (new_id, subdata["patient_gender"].upper(), subdata["patient_age"], subdata["patient_hyperT"], subdata["patient_hDisease"], subdata["patient_married"], subdata["patient_work_type"], subdata["patient_residence_type"], subdata["patient_avg_gLevel"], subdata["patient_bmi"], subdata["patient_smoked"], subdata["patient_stroke"]))
    database.commit()
    cursor.execute("INSERT INTO link_user_patient_data VALUES(%s, %s)", (userid, new_id,))
    database.commit()
    cursor.close()
    database.close()
    return new_id

'''Link commands'''
#Get
def link_get_all():
    links = []
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    cursor.execute("SELECT * FROM link_user_patient_data")
    for link in cursor.fetchall():
        links.append({
            "user_name": user_get_username(link[0]),
            "patient_id": link[1]
        })
    cursor.close()
    database.close()
    return links

def link_check_exists(userid):
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    print(userid, flush=True)
    cursor.execute("SELECT user_id FROM link_user_patient_data WHERE user_id = %s", (userid,))
    fetch = cursor.fetchall()
    cursor.close()
    database.close()
    if len(fetch) >= 1:
        return True
    else:
        return False

'''Admin commands'''
def admin_user_admin_check(username): ###DEPRECATED###
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    cursor.execute("SELECT user_admin FROM table_users WHERE user_email = %s", (str(username),))
    fetch = cursor.fetchall()
    cursor.close()
    database.close()
    if len(fetch) >= 1:
        if str(fetch[0][0]) == "1":
            return True
        else:
            return False
    return False

#Check
def admin_check_basepass():
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    cursor.execute("SELECT user_password FROM table_users WHERE user_id = 0")
    fetch = cursor.fetchall()
    cursor.close()
    database.close()
    if len(fetch) >= 1:
        if fetch[0][0] == "-1":
            return False
        else:
            return True
    else:
        return False

#Get
def admin_get_patient_data():
    patients = []
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    cursor.execute("SELECT * FROM table_patient_data")
    for patient in cursor.fetchall():
        patients.append({
            "id": patient[0],
            "user_link": None,
            "gender": patient[1],
            "age": patient[2], 
            "hypert": patient[3], 
            "hdisease": patient[4], 
            "married": patient[5], 
            "wtype": patient[6], 
            "rtype": patient[7], 
            "glevel": patient[8], 
            "bmi": patient[9], 
            "smoked": patient[10], 
            "stroke": patient[11], 
        })
    cursor.close()
    database.close()
    return patients

#Insert
#Update
def admin_hash_basepass():
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    admin_pass = string_hash("healthyadmin")
    cursor.execute("UPDATE table_users SET user_password = %s WHERE user_fullname = 'BaseAdmin'", (str(admin_pass),))
    database.commit()
    cursor.close()
    database.close()

def admin_apply_admin_user(user_id):
    status = True
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    cursor.execute("SELECT user_admin FROM table_users WHERE user_id = %s", (user_id,))
    if cursor.fetchall()[0][0] == 1:
        cursor.execute("UPDATE table_users SET user_admin = 0 WHERE user_id = %s", (user_id,))
        status = False
    else:
        cursor.execute("UPDATE table_users SET user_admin = 1 WHERE user_id = %s", (user_id,))
        status = True
    database.commit()
    cursor.close()
    database.close()
    return status

#Delete
def admin_delete_user(user_id):
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    if link_check_exists(user_id) is True:
        cursor.execute("DELETE FROM link_user_patient_data WHERE user_id = %s", (user_id,))
        database.commit()
    cursor.execute("DELETE FROM table_users WHERE user_id = %s", (user_id,))
    database.commit()
    cursor.close()
    database.close()