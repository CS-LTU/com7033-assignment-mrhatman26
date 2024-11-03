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
#This takes plain text and uses hashlib to hash said text.
#This website uses hashlib because the hashing remains consistent even when the website is restarted.
#The means users can still log in when the website is restarted.
#Python's default hash library does not do this and has inconsistent hashing between files, not just restarts.
#text = The text to hash. (String)

def str_to_bool(YesNo):
    if YesNo.upper() == "YES":
        return True
    else:
        return False
    #A simple function to convert "Yes" "No" strings to their boolean counterparts.
    #YesNo = The text to convert to a bool. (String)
    

'''User Commands'''
#Check
def user_check_exists(username):
    database = mysql.connector.connect(**get_db_config(deployed)) #Connect to the database using the settings defined in db_config.py.
    cursor = database.cursor() #Create a cursor for the database connection.
    cursor.execute("SELECT user_id FROM table_users WHERE user_email = %s", (str(username),)) #Execute the command to retrieve the user's ID using their email.
    if len(cursor.fetchall()) > 0: #If the length of what was returned is more than 0, the user exists so return True.
        cursor.close() #Close the cursor.
        database.close() #Close the connection to the database.
        return True
    else: #The user does not exist, return False.
        cursor.close()
        database.close()
        return False
    #This function checks if a user exists in the database or not. If they do, it returns True, else, it returns False.
    #username = The email of the user to check. (String)
    
def user_check_reconfirm(user_id):
    user = []
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    cursor.execute("SELECT user_id, user_fullname, user_admin FROM table_users WHERE user_id = %s", (str(user_id),))
    #Execute the command to retrieve the user's ID, name and admin status by using their user ID.
    for item in cursor.fetchall(): #Add their rertrieved data to the user list.
        user.append(item[0])
        user.append(item[1])
        user.append(item[2])
    cursor.close()
    database.close()
    return user #Return the user list.
    #This function checks to make sure the active user still exists by returning their ID, full name and if they are an admin or not.
    #This could be made more clear by turning the user list into a dictionary.
    #user_id = The ID of the user to check. (Integer)

def user_check_validate(userdata):
    if user_check_exists(userdata["username"]):
        database = mysql.connector.connect(**get_db_config(deployed))
        cursor = database.cursor()
        cursor.execute("SELECT user_password FROM table_users WHERE user_email = %s", (str(userdata["username"]),))
        #Execute the command to retrieve the user's password using their email. The password in the database is hashed and not plaintext.
        hashed_data = string_hash(userdata["password"]) #Hash the entered password.
        if hashed_data == cursor.fetchall()[0][0]: #Check if the hashed entered password is equal to the hashed password in the database. If it is, return True
            cursor.close()
            database.close()
            return True
        else: #The password is wrong, return False.
            return False
    else:
        return False
    #This fuction checks to see if the submitted user email exists and if the submitted password is correct.
    #Return True if both the email and password are correct and False if not.
    #userdata = A dictionary holding the submitted user email and password. (Dictionary)
    
#Get
def user_get_amount():
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    cursor.execute("SELECT user_id FROM table_users")
    #Execute the command to get all user IDs from the database.
    user_amount = len(cursor.fetchall()) #Get the length of the returned list.
    cursor.close()
    database.close()
    return user_amount
    #This function returns the amount of users currently in the database.
    #It takes no parameters.

def user_get_last_id():
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    cursor.execute("SELECT user_id FROM table_users")
    #Execute the command to get all user IDs from the database.
    last_id = cursor.fetchall()
    if len(last_id) >= 1: #If a user is in the database, return their ID + 1.
        last_id = last_id[-1][0] + 1
    else: #Else, return 0.
        last_id = 0
    cursor.close()
    database.close()
    return last_id
    #This function returns the ID of the last user in the database plus one. This is used for new user IDs.
    #It takes no parameters.

def user_get_id(username):
    user_id = None
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    cursor.execute("SELECT user_id FROM table_users WHERE user_email = %s", (str(username),))
    #Execute the command to get the user's ID from the database using their email.
    ids = cursor.fetchall()
    if len(ids) > 0: #If the returned list from the database is more than 0, return the ID, else return None.
        user_id = ids[0][0]
    cursor.close()
    database.close()
    return user_id
    #This function returns the ID of the user specified by using their email. If no ID is found, None is returned instead.
    #username = The email of the user who's ID is to be returned. (String)
                   
def user_get_all():
    user_list = []
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    cursor.execute("SELECT user_id, user_fullname, user_email, user_phone, user_admin FROM table_users")
    #Execute the command to get all user data from the database apart from their password.
    for user_data in cursor.fetchall(): #For each user in the returned list, add their data to the user_list list in the form of a dictionary.
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
    #This function returns all users in the database along with their information apart from their password.
    #This function takes no parameters.

def user_get_username(user_id):
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    cursor.execute("SELECT user_email FROM table_users WHERE user_id = %s", (user_id,))
    #Execute the command to get the email of the selected user using their ID.
    try:
        fetch = cursor.fetchall()[0][0] #Try to get their email.
    except:
        fetch = "Unknown User" #If no users with that ID are found, return "Unknown User" instead.
    cursor.close()
    database.close()
    return fetch
    #This function returns the email of the selected user using their ID to find them. It is basically the opposite of 'user_get_id'.
    #user_id = The ID of the user who's email is to be returned. (Integer)

def user_get_single(user_id):
    user_data = {}
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    cursor.execute("SELECT user_fullname, user_email, user_phone FROM table_users WHERE user_id = %s", (user_id,))
    #Execute the command to get the data of a single user apart from their paswwor.d
    for user_info in cursor.fetchall(): #Add the user's information to a dictionary.
        user_data["user_fullname"] = user_info[0]
        user_data["user_email"] = user_info[1]
        user_data["user_phone"] = user_info[2]
    return user_data
    #This function gets the data of a single user (apart from their password) using their user ID.
    #user_id = The ID of the user who's data is to be returned. (Integer)

#Insert
def user_create(userdata):
    if user_check_exists(userdata["email"]): #If the email of the new user is already in the database, return False.
        return False
    else:
        userdata["password"] = string_hash(userdata["password"]) #Hash the new user's password.
        userdata["id"] = user_get_last_id() #Get a new ID for the new user.
        database = mysql.connector.connect(**get_db_config(deployed))
        cursor = database.cursor()
        cursor.execute("INSERT INTO table_users VALUES(%s, %s, %s, %s, %s, %s)", (userdata["id"], str(userdata["fullname"]), userdata["password"], str(userdata["email"]), str(userdata["phone"]), 0))
        #Execute the command to create a new user in table_users with their information being taken from the userdata dictionary.
        database.commit()
        cursor.close()
        database.close()
        return True
        #This function attemtps to create a new user using the data specified in userdata. If the user already exists, False is returned to say that creation failed.
        #userdata = A dictionary that holds the information of the new user. (Dictionary)
    
#Update
def user_update(userdata):
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    if user_check_exists(userdata["email"]): #Check if the user exists.
        cursor.execute("SELECT user_id FROM table_users WHERE user_email = %s", (str(userdata["email"]),))
        #Get the user's ID.
        fetch = cursor.fetchall()
        if len(fetch) >= 1:
            if userdata["id"] != fetch[0][0]: #If the user's ID does not match the ID of user found, that means they are making their email the same as another user.
                #Return False if this is the case.
                return False
    old_userdata = user_get_single(userdata["id"]) #Get the user's old data.
    if userdata["fullname"] == "": #If any of the entered data is empty, make it equal the old data.
        userdata["fullname"] = old_userdata["user_fullname"]
    if userdata["email"] == "":
        userdata["email"] = old_userdata["user_email"]
    if userdata["phone"] == "":
        userdata["phone"] = old_userdata["user_phone"]
    if userdata["password"] == "": #If the password is empty, do not try to update it.
        cursor.execute("UPDATE table_users SET user_fullname = %s, user_email = %s, user_phone = %s WHERE user_id = %s", (str(userdata["fullname"]), str(userdata["email"]), str(userdata["phone"]), str(userdata["id"]),))
        #Update the user's information with the new data.
    else:
        userdata["password"] = string_hash(userdata["password"]) #Hash the new password.
        cursor.execute("UPDATE table_users SET user_fullname = %s, user_password = %s, user_email = %s, user_phone = %s WHERE user_id = %s", (str(userdata["fullname"]), str(userdata["password"]), str(userdata["email"]), str(userdata["phone"]), str(userdata["id"]),))
        #Update the user's information, but also update their password with the new one.
    database.commit()
    cursor.close()
    database.close()
    return True
    #This function updates a user's account with the new information they entered.
    #userdata = A dictionary that holds the new data to update the user with. (Dictionary)

'''Patient commands'''
#Get
def get_patient(patient_id):
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    cursor.execute("SELECT * FROM table_patient_data WHERE patient_id = %s", (patient_id,))
    #Get all of a patient's data using their ID.
    fetch = cursor.fetchall()
    cursor.close()
    database.close()
    if len(fetch) >= 1: #If the patient exists, return their information as an overly long dictionary.
        for patient in fetch:
            return {"patient_id": patient[0], "patient_gender": patient[1], "patient_age": patient[2], "patient_hyperT": patient[3], "patient_hDisease": patient[4], "patient_married": patient[5], "patient_work_type": patient[6], "patient_residence_type": patient[7], "patient_avg_gLevel": patient[8], "patient_bmi": patient[9], "patient_smoked": patient[10], "patient_stroke": patient[11]}
    else:
        #If the patient does not exist, return None.
        return None
    #This function returns the data of a patient as a dictionary using their ID to find them.
    #patient_id = The ID of the patient who's data is to be returned. (Integer)

#Insert
def insert_patient_data(patient_data):
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    cursor.execute("SELECT patient_id FROM table_patient_data")
    #Select all patient IDs from the database.
    fetch = cursor.fetchall()
    if len(fetch) >= 1: #If there are any IDs, save the ID but add one to it.
        new_id = int(fetch[-1][0]) + 1
    else: #If there are no IDs, save 0 instead.
        new_id = 0
    cursor.execute("INSERT INTO table_patient_data VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (str(new_id), str(patient_data["patient_gender"]), patient_data["patient_age"], str(patient_data["patient_hyperT"]), str(patient_data["patient_hDisease"]), str(patient_data["patient_married"]), str(patient_data["patient_work_type"]), str(patient_data["patient_residence_type"]), str(patient_data["patient_avg_gLevel"]), patient_data["patient_bmi"], str(patient_data["patient_smoked"]), str(patient_data["patient_stroke"]),))
    #Create a new patient with the submitted data.
    database.commit()
    cursor.close()
    database.close()
    return new_id
    #This function creates a new patient in table_patient_data using the data provided.
    #patient_data = A dictionary that holds the data of the new patient. (Dictionary)

def insert_new_patient_link(subdata, userid):
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    cursor.execute("SELECT patient_id FROM table_patient_data")
    fetch = cursor.fetchall()
    #Select all patient IDs from the database.
    if len(fetch) >= 1: #If there are any IDs, save the ID but add one to it.
        new_id = int(fetch[-1][0]) + 1
    else: #If there are no IDs, save 0 instead.
        new_id = 0
    cursor.execute("INSERT INTO table_patient_data VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (new_id, subdata["patient_gender"].upper(), subdata["patient_age"], subdata["patient_hyperT"], subdata["patient_hDisease"], subdata["patient_married"], subdata["patient_work_type"], subdata["patient_residence_type"], subdata["patient_avg_gLevel"], subdata["patient_bmi"], subdata["patient_smoked"], subdata["patient_stroke"]))
    #Insert the new patient into table_patient_data using the submitted data.
    database.commit()
    cursor.execute("INSERT INTO link_user_patient_data VALUES(%s, %s)", (userid, new_id,))
    #Create a link between the user and patient using both IDs.
    database.commit()
    cursor.close()
    database.close()
    return new_id
    #This function creates a new patient, but unlike the previous function, it creates a link between a user and said patient.
    #subdata = A dictionary that holds the data for the new patient. (Integer)
    #userid = The ID of the user to link the patient to. (Integer)

#Update
def update_patient(subdata, patient_id):
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    cursor.execute("UPDATE table_patient_data SET patient_gender = %s, patient_age = %s, patient_hyperT = %s, patient_hDisease = %s, patient_married = %s, patient_work_type = %s, patient_residence_type = %s, patient_avg_gLevel = %s, patient_bmi = %s, patient_smoked = %s, patient_stroke = %s WHERE patient_id = %s", (subdata["patient_gender"], subdata["patient_age"], subdata["patient_hyperT"], subdata["patient_hDisease"], subdata["patient_married"], subdata["patient_work_type"], subdata["patient_residence_type"], subdata["patient_avg_gLevel"], subdata["patient_bmi"], subdata["patient_smoked"], subdata["patient_stroke"], patient_id,))
    #Update the patient with the new data.
    database.commit()
    cursor.close()
    database.close()
    #This function updates the patient with new data. 
    #subdata = A dictionary that holds the data to update the patient with. (Integer)
    #patient_id = The ID of the patient to update. (Integer)

'''Link commands'''
#Check
def link_check_exists(id, is_patient_id):
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    if is_patient_id is False:
        cursor.execute("SELECT user_id FROM link_user_patient_data WHERE user_id = %s", (id,))
        #If is_patient_id is False, return any links the user has to any patient data.
    else:
        cursor.execute("SELECT patient_id FROM link_user_patient_data WHERE patient_id = %s", (id,))
        #If is_patient_id is True, return instead any links a patient has to any users.
    fetch = cursor.fetchall()
    cursor.close()
    database.close()
    if len(fetch) >= 1: #If any links are found, return True, else return False.
        return True
    else:
        return False
    #This function checks if there are any links between users and patients.
    #id = The ID of user or patient to check. (Integer)
    #is_patient_id = Whether or not the ID provided is a patient_id or a user_id. (Boolean)

#Get
def link_get_all():
    links = []
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    cursor.execute("SELECT * FROM link_user_patient_data")
    #Get all links from the database.
    for link in cursor.fetchall():
        links.append({ #Save each link to the links list as a dictionary.
            "user_name": user_get_username(link[0]),
            "patient_id": link[1]
        })
    cursor.close()
    database.close()
    return links
    #This function returns all links in the database as a list of dictionaries.
    #This function takes no parameters.

def link_get(user_id):
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    cursor.execute("SELECT * FROM link_user_patient_data WHERE user_id = %s", (user_id, ))
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