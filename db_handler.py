from os import stat
import mysql.connector
import hashlib
from db_config import get_db_config
from mongodb import mongo_nuke

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
    if user_check_exists(userdata["username"]):
        database = mysql.connector.connect(**get_db_config(deployed))
        cursor = database.cursor()
        cursor.execute("SELECT user_password FROM table_users WHERE user_email = %s", (str(userdata["username"]),))
        hashed_data = string_hash(userdata["password"])
        print(hashed_data)
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
#Get
def get_patient(patient_id):
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    cursor.execute("SELECT * FROM table_patient_data WHERE patient_id = %s", (patient_id,))
    fetch = cursor.fetchall()
    cursor.close()
    database.close()
    if len(fetch) >= 1:
        for patient in fetch:
            return {"patient_id": patient[0], "patient_gender": patient[1], "patient_age": patient[2], "patient_hyperT": patient[3], "patient_hDisease": patient[4], "patient_married": patient[5], "patient_work_type": patient[6], "patient_residence_type": patient[7], "patient_avg_gLevel": patient[8], "patient_bmi": patient[9], "patient_smoked": patient[10], "patient_stroke": patient[11]}
    else:
        return None

#Insert
def insert_patient_data(patient_data):
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

def insert_new_patient_link(subdata, userid):
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

#Update
def update_patient(subdata, patient_id):
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    cursor.execute("UPDATE table_patient_data SET patient_gender = %s, patient_age = %s, patient_hyperT = %s, patient_hDisease = %s, patient_married = %s, patient_work_type = %s, patient_residence_type = %s, patient_avg_gLevel = %s, patient_bmi = %s, patient_smoked = %s, patient_stroke = %s WHERE patient_id = %s", (subdata["patient_gender"], subdata["patient_age"], subdata["patient_hyperT"], subdata["patient_hDisease"], subdata["patient_married"], subdata["patient_work_type"], subdata["patient_residence_type"], subdata["patient_avg_gLevel"], subdata["patient_bmi"], subdata["patient_smoked"], subdata["patient_stroke"], patient_id,))
    database.commit()
    cursor.close()
    database.close()

'''Link commands'''
#Check
def link_check_exists(id, is_patient_id):
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    if is_patient_id is False:
        cursor.execute("SELECT user_id FROM link_user_patient_data WHERE user_id = %s", (id,))
    else:
        cursor.execute("SELECT patient_id FROM link_user_patient_data WHERE patient_id = %s", (id,))
    fetch = cursor.fetchall()
    cursor.close()
    database.close()
    if len(fetch) >= 1:
        return True
    else:
        return False
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

def link_get(user_id):
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    cursor.execute("SELECT * FROM link_user_patient_data")
    fetch = cursor.fetchall()
    cursor.close()
    database.close()
    if len(fetch) >= 1:
        return {"user_id": fetch[0][0], "patient_id": fetch[0][1]}
    else:
        return None
    
def link_delete(user_id): #Unused apart from in testing
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    cursor.execute("DELETE FROM link_user_patient_data WHERE user_id = %s", (user_id,))
    database.commit()
    cursor.close()
    database.close()


'''Admin commands'''
def admin_user_admin_check(username):
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
    if link_check_exists(user_id, False) is True:
        cursor.execute("DELETE FROM link_user_patient_data WHERE user_id = %s", (user_id,))
        database.commit()
    cursor.execute("DELETE FROM table_users WHERE user_id = %s", (user_id,))
    database.commit()
    cursor.close()
    database.close()

def admin_delete_patient_data(patient_id):
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    if link_check_exists(patient_id, True):
        cursor.execute("DELETE FROM link_user_patient_data WHERE patient_id = %s", (patient_id,))
        database.commit()
    cursor.execute("DELETE FROM table_patient_data WHERE patient_id = %s", (patient_id,))
    database.commit()
    cursor.close()
    database.close()

def admin_user_nuke():
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    cursor.execute("SELECT user_id FROM table_users")
    for user in cursor.fetchall():
        if link_check_exists(user[0], False) is True:
            link_delete(user[0])
    cursor.execute("DELETE FROM table_users WHERE user_email != %s", ("baseadmin@example.com",))
    database.commit()
    cursor.close()
    database.close()

def admin_patient_nuke():
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    cursor.execute("SELECT patient_id FROM table_patient_data")
    fetch = cursor.fetchall()
    length = len(fetch)
    index = 0
    for patient in fetch:
        if link_check_exists(patient[0], True):
            cursor.execute("DELETE FROM link_user_patient_data WHERE patient_id = %s", (patient[0],))
            database.commit()
        print(str(index) + "/" + str(length) + " patient records deleted", end="\r", flush=True)
        index += 1
    cursor.execute("DELETE FROM table_patient_data WHERE 1=1")
    database.commit()
    cursor.close()
    database.close()
    print(str(length) + "/" + str(length) + " patient records deleted", flush=True)

def admin_link_nuke():
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    cursor.execute("DELETE FROM link_user_patient_data WHERE 1=1")
    database.commit()
    cursor.close()
    database.close()

def admin_nuke(m_client):
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    cursor.execute("DELETE FROM link_user_patient_data WHERE 1=1")
    database.commit()
    cursor.execute("DELETE FROM table_users WHERE user_email != %s", ("baseadmin@example.com", ))
    database.commit()
    cursor.execute("DELETE FROM table_patient_data WHERE 1=1")
    database.commit()
    cursor.close()
    database.close()
    mongo_nuke(m_client)

def admin_dump_data():
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    cursor.execute("SELECT * FROM table_users")
    fetch = cursor.fetchall()
    length = len(fetch)
    index = 0
    file = open("static/dumps/table_users.txt", "w")
    for user in fetch:
        for user_data in user:
            user_data = str(user_data) + ", "
            file.write(user_data)
        file.write("\n")
        print(str(index) + "/" + str(length) + " users saved to table_users.txt", end="\r", flush=True)
        index += 1
    file.close()
    print(str(length) + "/" + str(length) + " users saved to table_users.txt", flush=True)
    cursor.execute("SELECT * FROM table_patient_data")
    fetch = cursor.fetchall()
    length = len(fetch)
    index = 0
    file = open("static/dumps/table_patient_data.txt", "w")
    for patient in fetch:
        for patient_data in patient:
            patient_data = str(patient_data) + ", "
            file.write(patient_data)
        file.write("\n")
        print(str(index) + "/" + str(length) + " patients saved to table_patient_data.txt", end="\r", flush=True)
        index += 1
    file.close()
    print(str(length) + "/" + str(length) + " patients saved to table_patient_data.txt", flush=True)
    cursor.execute("SELECT * FROM link_user_patient_data")
    fetch = cursor.fetchall()
    length = len(fetch)
    index = 0
    file = open("static/dumps/link_user_patient_data.txt", "w")
    for link in fetch:
        for link_data in link:
            link_data = str(link_data) + ", "
            file.write(link_data)
        file.write("\n")
        print(str(index) + "/" + str(length) + " links saved to link_user_patient_data.txt", end="\r", flush=True)
        index += 1
    file.close()
    print(str(length) + "/" + str(length) + " links saved to link_user_patient_data.txt", flush=True)
    print("All tables have been dumped to the /static/dumps/ directory", flush=True)