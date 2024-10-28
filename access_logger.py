import datetime as dt
def get_time():
    current_time = dt.datetime.now()
    return str("[" + current_time.strftime("%Y.%m.%d at %H:%M:%S") + "]")

def add_access_log(ip, user, wwAccessed, failed, admin):
    log_file = open("static/logs.txt", "at")
    current_time = dt.datetime.now()
    text = "\n" + get_time()
    if admin is False:
        if failed is False:
            text = text + ": " + ip + " (User: " + user + ") successfully accessed " + wwAccessed
        else:
            text = text + ": " + ip + " (User: " + user + ") FAILED to access " + wwAccessed
    else:
        if failed is False:
            text = text + " (ADMIN): " + ip + " (User: " + user + ") successfully accessed Admin resource " + wwAccessed
        else:
            text = text + " (ADMIN): " + ip + " (User: " + user + ") FAILED to access Admin resource " + wwAccessed
    log_file.write(text)
    log_file.close()

def add_new_user_log(ip, newUser, failed):
    log_file = open("static/logs.txt", "at")
    current_time = dt.datetime.now()
    text = "\n" + get_time()
    if failed is False:
        text = text + ": " + ip + " successfully created new user with username of " + newUser
    else:
        text = text + ": " + ip + " FAILED to create new user with username " + newUser
    log_file.write(text)
    log_file.close()

def add_modify_user_log(ip, username, failed):
    log_file = open("static/logs.txt", "at")
    current_time = dt.datetime.now()
    text = "\n" + get_time()
    if failed is False:
        text = text + ": " + ip + " successfully modified the account of " + username
    else:
        text = text + ": " + ip + " FAILED to modified the account of " + username
    log_file.write(text)
    log_file.close()

def add_delete_user_log(ip, username, failed, admin):
    log_file = open("static/logs.txt", "at")
    current_time = dt.datetime.now()
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

def add_login_log(ip, username, failed, logout):
    log_file = open("static/logs.txt", "at")
    current_time = dt.datetime.now()
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

def add_user_admin_log(ip, username, failed):
    log_file = open("static/logs.txt", "at")
    current_time = dt.datetime.now()
    text = "\n" + get_time()
    if failed is False:
        text = text + " (ADMIN): " + ip + " successfully made " + username + " an Admin"
    else:
        text = text + " (ADMIN): " + ip + " FAILED to make " + username + " an Admin"
    log_file.write()
    log_file.close()

def add_readDB_admin_log(ip, username):
    log_file = open("static/logs.txt", "at")
    current_time = dt.datetime.now()
    text = "\n" + get_time()
    text = text + " (ADMIN): " + ip + "(User: " + username + " loaded the database from healthcare-dataset-stroke-data.csv"
    log_file.write(text)
    log_file.close()