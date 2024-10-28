import datetime as dt
def get_time():
    current_time = dt.datetime.now()
    return str("[" + current_time.strftime("%Y.%m.%d at %H:%M:%S") + "]")

def add_access_log(ip, user, wwAccessed, failed, admin):
    log_file = open("/static/logs.txt", "at")
    current_time = dt.datetime.now()
    text = get_time()
    if admin is False:
        if failed is False:
            text = text + ": " + ip + " (User: " + user + ") successfully accessed " + wwAccessed
        else:
            text = text + ": " + ip + " (User: " + user + ") FAILED to access " + wwAccessed
    else:
        if failed is False:
            text = text + ": " + ip + " (User: " + user + ") successfully accessed Admin resource " + wwAccessed
        else:
            text = text + ": " + ip + " (User: " + user + ") FAILED to access Admin resource " + wwAccessed
    log_file.write(text)
    log_file.close()

def add_new_user_log(ip, newUser, failed):
    log_file = open("/static/logs.txt", "at")
    current_time = dt.datetime.now()
    text = get_time()
    if failed is False:
        text = text + ": " + ip + " created new user with username of " + newUser
    else:
        text = text + ": " + ip + " FAILED to create new user with username " + newUser
    log_file.write(text)
    log_file.close()