import datetime as dt
'''This is the access_logger.
It is used to log all pages users access and actions they make.
All logs are saved to the static folder in "logs.txt"
'''

def get_time():
    current_time = dt.datetime.now()
    return str("[" + current_time.strftime("%Y.%m.%d at %H:%M:%S") + "]")
    #This function gets the current time, formats it to 'Year.Month.Data at Hour:Minute:Second' and returns it.

def add_error_log(ip, user, wFailed, theException=None):
    log_file = open("static/logs.txt", "at") #Open the log file for appending in text mode.
    text = "\n" + get_time() #Creates a variable called text to hold the message that will be saved. Adds the current time to it after a new line.
    #theException is an optional argument.
    if theException is None:
        text = text + ": " + ip + " (User: " + user + ") encountered the following error: " + wFailed + "\nNo exception information available."
        #Add a log that states the time, the ip address and user that was given and what failed.
    else:
        text = text + ": " + ip + " (User: " + user + ") encountered the following error: " + wFailed + "\nException:\n" + str(theException)
        #Add a similar log, but show the exception given
    log_file.write(text) #Write the message to the log file.
    log_file.close() #Close the file you fool!
    #This function adds an error log that show when an error occurred, the user (and IP) that caused it and, if given, the exact exception that is associated with the error.
    #ip = The IP address of the user that accessed this function. (String)
    #user = The email of the user that accessed this function. (String)
    #wFailed = What Failed = A string that gives a basic description of what went wrong. (String)
    #theException = An Exception that holds the actual error message. This parameter is optional and is None if not given. (Exception or None)

#Most of this Python file is repetitive, so I will only comment unique lines of code. 
def add_access_log(ip, username, wwAccessed, failed, admin):
    log_file = open("static/logs.txt", "at")
    text = "\n" + get_time()
    if admin is False:
        if failed is False:
            text = text + ": " + ip + " (User: " + username + ") successfully accessed " + wwAccessed
        else:
            text = text + ": " + ip + " (User: " + username + ") FAILED to access " + wwAccessed
    else:
        if failed is False:
            text = text + " (ADMIN): " + ip + " (User: " + username + ") successfully accessed Admin resource " + wwAccessed
        else:
            text = text + " (ADMIN): " + ip + " (User: " + username + ") FAILED to access Admin resource " + wwAccessed
    log_file.write(text)
    log_file.close()
    #This function adds a simple access log. It shows who accessed what and if what was accessed was related to admin pages in any way.
    #ip = The IP address of the user that accessed this function. (String)
    #username = The email of the user that accessed this function. (String)
    #wwAccessed = What Was Accessed = The directory that was accessed. (String)
    #failed = If the access was failed. Shows 'FAILED' instead of 'successfully' in the logs. (Boolean)
    #admin = If the access was realted to admin pages in any way. (Boolean)

def add_new_user_log(ip, newUser, failed):
    log_file = open("static/logs.txt", "at")
    text = "\n" + get_time()
    if failed is False:
        text = text + ": " + ip + " successfully created new user with username of " + newUser
    else:
        text = text + ": " + ip + " FAILED to create new user with username " + newUser
    log_file.write(text)
    log_file.close()
    #This function adds a new user log. It shows if a new user was created successfully, along with the new user's username, and by what IP.
    #ip = The IP address of the user that accessed this function. (String)
    #newUser = The email of the new user that was created. (String)
    #failed = If the new user failed to be created or not. Shows 'FAILED' instead of 'successfully' in the logs. (Boolean)

def add_modify_user_log(ip, username, failed):
    log_file = open("static/logs.txt", "at")
    text = "\n" + get_time()
    if failed is False:
        text = text + ": " + ip + " successfully modified the account of " + username
    else:
        text = text + ": " + ip + " FAILED to modified the account of " + username
    log_file.write(text)
    log_file.close()
    #This function adds a modified user log. It shows if a user was modified successfully along with their old email. Also shows the IP that tried to modify the user.
    #ip = The IP address of the user that accessed this function. (String)
    #username = The old email of the user that was modified. (String)
    #failed = If the modification failed or not. Shows 'FAILED' instead of 'successfully' in the logs. (Boolean)

def add_delete_user_log(ip, username, failed, admin):
    log_file = open("static/logs.txt", "at")
    text = "\n" + get_time()
    if admin is False:
        if failed is False:
            text = text + ": " + ip + " successfully deleted the account of " + username
        else:
            text = text + ": " + ip + " FAILED to delete the account of " + username
    else:
        if failed is False:
            text = text + " (ADMIN): " + ip + " successfully deleted the account of " + username
        else:
            text = text + " (ADMIN): " + ip + " FAILED to delete the account of " + username
    log_file.write(text)
    log_file.close()
    #This function adds a user delete log. It shows if a user was deleted successfully or not and if an admin deleted it or the user themself.
    #ip = The IP address of the user that accessed this function. (String)
    #username = The email of the user that is being deleted. (String)
    #failed = If the deletion failed or not. Shows 'FAILED' instead of 'successfully' in the logs. (Boolean)
    #admin = If the deletion was by an admin or not. Shows '(ADMIN)' in the logs if True. (Boolean)

def add_login_log(ip, username, failed, logout):
    log_file = open("static/logs.txt", "at")
    text = "\n" + get_time()
    if failed is False:
        if logout is False:
            text = text + ": " + ip + " successfully logged in as " + username
        else:
            text = text + ": " + ip + " (User: " + username + ") successfully logged out of their account"
    else:
        if logout is False:
            text = text + ": " + ip + " FAILED to log in as " + username
        else:
            text = text + ": " + ip + " (User: " + username + ") FAILED to log out of their account"
    log_file.write(text)
    log_file.close()
    #This function adds a user log in log (loginloginloginloginlo-). It shows if a user logged in or out and if the login/logout failed.
    #ip = The IP address of the user that accessed this function. (String)
    #username = The email of the user logging in. (String)
    #failed = If the login failed or not. Shows 'FAILED' instead of 'successfully' in the logs. (Boolean)
    #logout = If the user is logging out or not. If True, it will show "logged out" instead of "logged in" in the logs. (Boolean)

def add_new_patient_log(ip, username, failed, is_mongodb):
    log_file = open("static/logs.txt", "at")
    text = "\n" + get_time()
    if failed is False:
        if is_mongodb is False:
            text = text + ": " + ip + " successfully added new patient data to MySQL with a link to " + username
        else:
            text = text + ": " + ip + " successfully added new patient data to MongoDB"
    else:
        if is_mongodb is False:
            text = text + ": " + ip + " FAILED to add new patient data to MySQL with a link to " + username
        else:
            text = text + ": " + ip + " FAILED to add new patient data to MongoDB"
    log_file.write(text)
    log_file.close()
    #This function adds a new patient log. It shows when a new patient is created and if the creation failed or not. It also shows which database the data was written to.
    #ip = The IP address of the user that accessed this function. (String)
    #username = The email of the user attempting to create the patient. (String)
    #failed = If the creation of the patient failed or not. Shows 'FAILED' instead of 'successfully' in the logs. (Boolean)
    #is_mongodb = If the data was saved to mongodb or not. Shows "to MongoDB" instead of "to MySQL" in the logs if True. (Boolean)

def add_modify_patient_log(ip, username, failed, is_mongodb, patient_id):
    log_file = open("static/logs.txt", "at")
    text = "\n" + get_time()
    if failed is False:
        if is_mongodb is False:
            text = text + ": " + ip + " (User: " + username + ") successfully modified patient data with ID of " + str(patient_id) + " in MySQL"
        else:
            text = text + ": " + ip + " (User: " + username + ") successfully modified patient data with ID of " + str(patient_id) + " in MongoDB"
    else:
        if is_mongodb is False:
            text = text + ": " + ip + " (User: " + username + ") failed to modify patient data with ID of " + str(patient_id) + " in MySQL"
        else:
            text = text + ": " + ip + " (User: " + username + ") failed to modify patient data with ID of " + str(patient_id) + " in MongoDB"
    log_file.write(text)
    log_file.close()
    #This function add a new modified patient log. It shows when a patient is attempted to be modified. It also shows if the patient was modified from mongodb or MySQL.
    #This log is automatically (ADMIN)
    #ip = The IP address of the user that accessed this function. (String)
    #username = The email of the user attempting to modify the patient. (String)
    #failed = If the modification of the patient failed or not. Shows 'FAILED' instead of 'successfully' in the logs. (Boolean)
    #is_mongodb = If the data was modified in mongodb or not. Shows "in MongoDB" instead of "in MySQL" in the logs if True. (Boolean)
    #patient_id = The id of the patient being updated. (Integer)

def add_user_admin_log(ip, username, failed, reverse):
    log_file = open("static/logs.txt", "at")
    text = "\n" + get_time()
    if failed is False:
        if reverse is False:
            text = text + " (ADMIN): " + ip + " successfully made " + username + " an Admin"
        else:
            text = text + " (ADMIN): " + ip + " successfully removed Admin status from " + username
    else:
        if reverse is False:
            text = text + " (ADMIN): " + ip + " FAILED to make " + username + " an Admin"
        else:
            text = text + " (ADMIN): " + ip + " FAILED to remove Admin status from " + username
    log_file.write(text)
    log_file.close()
    #This function adds a new modified admin status log. It shows when a user has been made an admin or had admin access revoked.
    #This log is automatically (ADMIN)
    #ip = The IP address of the user that accessed this function. (String)
    #username = The email of the user having their admin status modified. (String)
    #failed = If the modification was successful or not. Shows 'FAILED' instead of 'successfully' in the logs. (Boolean)
    #reverse = If the admin access is being revoked or not. Shows 'removed' instead of 'made' if True. (Boolean)

def add_readDB_admin_log(ip, username):
    log_file = open("static/logs.txt", "at")
    text = "\n" + get_time()
    text = text + " (ADMIN): " + ip + " (User: " + username + ") loaded the database from healthcare-dataset-stroke-data.csv"
    log_file.write(text)
    log_file.close()
    #This function adds a new database read log. It shows when a user loads data from healthcare-dataset-stroke-data.csv into MySQL and MongoDN.
    #This log is automatically (ADMIN)
    #ip = The IP address of the user that accessed this function. (String)
    #username = The user name of the user that accessed this function. (String)

def add_delete_db_log(ip, username, is_mongodb, patient_id, admin):
    log_file = open("static/logs.txt", "at")
    text = "\n" + get_time()
    if admin is True:
        if is_mongodb is False:
            text = text + "(ADMIN): " + ip + " (User: " + username + ") " + "successfully deleted patient data from MySQL (Deleted patient_id was " + str(patient_id) + ")"
        else:
            text = text + "(ADMIN): " + ip + " (User: " + username + ") " + "successfully deleted patient data from MongoDB (Deleted MySQL_ID was " + str(patient_id) + ")"
    else:
        if is_mongodb is False:
            text = text + ": " + ip + " (User: " + username + ") " + "successfully deleted patient data from MySQL (Deleted patient_id was " + str(patient_id) + ")"
        else:
            text = text + ": " + ip + " (User: " + username + ") " + "successfully deleted patient data from MongoDB (Deleted MySQL_ID was " + str(patient_id) + ")"
    log_file.write(text)
    log_file.close()
    #This function adds a new deleted patient log. It shows when a patient is attempted to be deleted. It also shows if the patient was deleted from mongodb or MySQL.
    #This log is automatically (ADMIN)
    #ip = The IP address of the user that accessed this function. (String)
    #username = The email of the user attempting to delete the patient. (String)
    #is_mongodb = If the data was modified in mongodb or not. Shows "in MongoDB" instead of "in MySQL" in the logs if True. (Boolean)
    #patient_id = The id of the patient being deleted. (Integer)
    #admin = If the patient was deleted by an admin or not. (Boolean)

def add_admin_nuke_log(ip, username, wwDeleted, everything):
    log_file = open("static/logs.txt", "at")
    text = "\n" + get_time()
    if everything is False:
        text = text + "(ADMIN): " + ip + " (User: " + username + ") " + " deleted all data in " + wwDeleted
    else:
        text = text + "(!!!!ADMIN_NUKE!!!!):  " + ip + " (User: " + username + ") deleted ALL data from ALL tables"
    log_file.write(text)
    log_file.close()
    #This function adds a admin nuke log. This shows when an admin choses to delete ALL data from one or every table. This log should be very, very rare.
    #ip = The IP address of the user that accessed this function. (String)
    #username = The email of the user attempting to delete the data. (String)
    #wwDeleted = What Was Deleted = Which of the tables was deleted. (String)
    #everything = If ALL tables had their data deleted or not. Will add '(!!!!ADMIN_NUKE!!!!)' to log if True. (Boolean)

def add_admin_dump_log(ip, username):
    log_file = open("static/logs.txt", "at")
    text = "\n" + get_time()
    text = text + "(ADMIN): " + ip + " (User: " + username + ") " + " dumped all database data"
    log_file.write(text)
    log_file.close()
    #This function adds a dump log. This shows when an admin chose to dump all data from every table.
    #ip = The IP address of the user that accessed this function. (String)
    #username = The username of the user attempting to dump the data. (String)