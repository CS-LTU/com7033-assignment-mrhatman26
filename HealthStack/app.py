import ast
from flask import Flask, render_template, url_for, request, redirect, abort
from flask_login import LoginManager, current_user, login_user, logout_user
from user import User
from db_handler import *
from access_logger import *
from mongodb import *
from misc import clean_subdata

'''Server Vars'''
app = Flask(__name__) #Create the flask application
app.secret_key = "HealthyIGuess" #The secret key used to store user data. In future, I should randomise this.
deployed = False #If this application is deployed or not. If not, it is considered to be being debugged/developed.
if deployed is False:
    m_client = pymongo.MongoClient("mongodb://localhost:27017") #Open a socket connection to the mongodb database.
else:
    m_client = pymongo.MongoClient("mongodb:27017", username='user', password='pass') #Open a socket connection to the mongodb database.
#Note: The mongodb connection is created here as opening it too many times exhausts available sockets.
#This is hard to do normally, but with the volume of the data we are adding, it happens easily. Weirdly, this problem is more common when using pytest?

'''Login Manager'''
login_manager = LoginManager() #Creates an instance of the Flask-Login LoginManager that handles user logging in, out and keeping them logged in.
login_manager.init_app(app) #Binds the LoginManager to this Flask application.
@login_manager.user_loader
def load_fuser(id):
    user_check = user_check_reconfirm(id)
    if len(user_check) <= 0:
        return None
    else:
        return User(user_check[0], user_check[1], bool(user_check[2]))
#This is run everytime a page is loaded. It keeps the user logged in by reconfirming their ID. If the user no longer exists though, they are automatically logged out.
#The login manager provides the base User through UserMixin which has many attributes, but the ones for my users are:
#id = The ID of the user
#username = The full name of the user. Not their email.
#is_admin = If the user is an admin or not.
    
def log_get_user():
    if hasattr(current_user, 'username'):
        return current_user.username
    else:
        return "Annonymous"
    #Checks the current_user (provided by the LoginManager) and if it has the username attribute.
    #If it does, then the user is logged in so we can safely return their username.
    #If it doesn't, the the user is not logged in so we return a placeholder string of "Annonymous".

'''General Routes'''
#Home/Index
#Defines a route. Routes are, essentially, the directories of the server the website is running on. This is the root, or, home directory.
#All other routes are subdirectories of the root directory.
@app.route('/')
def home():
    if admin_check_basepass() is False:
        admin_hash_basepass()
    #This checks if the baseadmin has had their password hashed or not.
    #If not, their password is hashed and added to their database entry.
    add_access_log(request.remote_addr, log_get_user(), "/ (home)", False, False)
    #Add a log to show that this page has been accessed, who accessed it and that it has neither failed nor is an admin page.
    return render_template('home.html', page_name="Home")
#This is the home page. It shows the standard for most of my routes.
#That is: We return a render_template using my HTML pages and provide those pages the variable "page_name" which is shown in the browsers tabs using the title tag.

#Data Submission
@app.route('/submission/')
def submission():
    if current_user.is_authenticated: #Make sure the user is logged in.
        add_access_log(request.remote_addr, log_get_user(), "/submission/ (submission)", False, False)
        return render_template('submission.html', page_name="Submission", already_submitted=link_check_exists(current_user.id, False))
    else: #If the user is not logged in, create a failed access log and redirect the user to the login page.
        add_access_log(request.remote_addr, log_get_user(), "/submission/ (submission)", True, False)
        return redirect('/users/login/')
#This is the data submission page. Here, the user is able to submit their patient data.
@app.route('/submission/validate/', methods=['POST'])
def submission_validate():
    if current_user.is_authenticated:
        subdata = request.get_data() #Get the data sent from submission.js
        subdata = subdata.decode() #Decode the data from binary to plaintext.
        subdata = ast.literal_eval(subdata) #Convert the data into a dictionary.
        add_access_log(request.remote_addr, log_get_user(), "/submission/validate/ (submission_validate)", False, False)
        mysql_done = False #MySQL gets the data first. Once it gets said data, this variable is changed to True
        try: #Try the following lines, if any fail, run the except code.
            clean_subdata(subdata) #Make sure the data is how we want it to be. (E.G: Make sure Yes/No values are instead 1/0)
            mysql_id = insert_new_patient_link(subdata, current_user.id) #Insert the data into MySQL and retrieve the MySQL ID of the data.
            subdata["MySQL_ID"] = mysql_id #Add the MySQL ID to the dictionary that holds the data.
            mysql_done = True #Change mysql_done to True to show that we are now adding the data to MongoDB rather than MySQL.
            add_new_patient_log(request.remote_addr, log_get_user(), False, False) #Add a new patient log to show that a new patient was created in MySQL.
            mongo_insert(subdata, m_client) #Add the data to MongoDB using m_client to connect.
            add_new_patient_log(request.remote_addr, log_get_user(), False, True) #Add a new patient log to show that a new patient was created in MongoDB.
            return "success" #Return the string "success" to submission.js to let JavaScript know to redirect.
        except Exception as e: #One of the previous lines failed, run these instead while saving the Exception that occurred as the variable 'e'.
            add_new_patient_log(request.remote_addr, log_get_user(), True, mysql_done) #Add a new failed patient log and show which database failed.
            add_error_log(request.remote_addr, log_get_user(), "Submission data insertion failed.", e) #Add an error log and provide it with the Exception that ocurred.
            return "servererror" #Return the string "servererror" to submission.js to let JavaScript know that an error ocurred and to show an error on the page.
    else: #The user is not authenticated. Redirect to the login page.
        add_access_log(request.remote_addr, log_get_user(), "/submission/validate/ (submission_validate)", True, False)
        return redirect('/users/login/')
    #This is the submission validation page. It processes the data and adds it to MySQL and MongoDB.
    #Note: For any routes that I consider to be linked in any way, I have avoided adding new lines between them so they are together.
    
@app.route('/data/view/')
def view_data():
    if current_user.is_authenticated:
        add_access_log(request.remote_addr, log_get_user(), "/data/view/ (view_data)", False, False)
        return render_template('data.html', page_name="Submitted Data", patient_data=mongo_find_all(False, m_client))
    else:
        add_access_log(request.remote_addr, log_get_user(), "/data/view/ (view_data)", True, False)
        return redirect('/users/login/')
    #This is the data view page. It shows logged in users the patient data currently in the MongoDB database. This version of the data is not linked to users
    #and is thus more annonymous.
    
'''User Routes'''
#Login
@app.route('/users/login/')
def user_login():
    if current_user.is_authenticated:
        add_access_log(request.remote_addr, log_get_user(), "/users/login/ (user_login)", True, False)
        return redirect('/')
    else:
        add_access_log(request.remote_addr, log_get_user(), "/users/login/ (user_login)", False, False)
        return render_template('users/login.html', page_name="Login")
    #The login page. It allows the user to enter their email and password to try to log in.
@app.route('/users/login/validate/', methods=['POST'])
def user_login_validate():
    if current_user.is_authenticated: #If the user is already logged in and happens to go back to the login page, redirect them to the home page.
        add_access_log(request.remote_addr, log_get_user(), "/users/login/validate/ (user_login_validate)", True, False)
        return redirect('/')
    else:
        userdata = request.get_data() #Get the data, decode it and make it a dictionary as in the previous route.
        userdata = userdata.decode()
        userdata = ast.literal_eval(userdata)
        add_access_log(request.remote_addr, log_get_user(), "/users/login/validate/ (user_login_validate)", False, False)
        try:
            if user_check_validate(userdata) is True: #If the user email and password are correct, log them in.
                login_user(User(user_get_id(userdata["username"]), userdata["username"], admin_user_admin_check(userdata["username"])))
                #Log the user in using the User class. The admin_user_admin_check function checks to see if the user is an admin or not.
                add_login_log(request.remote_addr, userdata["username"], False, False)
                #Add a successful login log.
                return "success"
            else:
                add_login_log(request.remote_addr, userdata["username"], True, False)
                #Add a failed login log.
                return "usernotexist" #Return the string "usernotexist" to login.js to show that an error ocurred in which the user does not exist or the password is wrong.
        except Exception as e:
            add_login_log(request.remote_addr, userdata["username"], True, False)
            add_error_log(request.remote_addr, log_get_user(), "Login user fail", e)
            return "servererror"
    #The login validation page. It checks if the entered user email and password are correct and, if they are, the user is logged in.

#Signup
@app.route('/users/signup/')
def user_signup():
    if current_user.is_authenticated:
        add_access_log(request.remote_addr, log_get_user(), "/users/signup/ (user_signup)", True, False)
        return redirect('/')
    else:
        add_access_log(request.remote_addr, log_get_user(), "/users/signup/ (user_signup)", False, False)
        return render_template('users/signup.html', page_name="Signup")
    #The signup page. It requests the user's name, email, password and phone number.
@app.route('/users/signup/validate/', methods=['POST'])
def user_signup_validate():
    if current_user.is_authenticated: #If the user is already logged in, they don't need to signup again, so redirect them to the home page.
        add_access_log(request.remote_addr, log_get_user(), "/users/signup/validate/ (user_signup_validate)", True, False)
        return redirect('/')
    else:
        userdata = request.get_data() #Get the data, decode it and make it a dictionary as in the previous routes.
        userdata = userdata.decode()
        userdata = ast.literal_eval(userdata)
        add_access_log(request.remote_addr, log_get_user(), "/users/signup/validate/ (user_signup_validate)", False, False)
        try:
            if user_create(userdata) is True: #If the new user was successfully created, return the string "success" to signup.js
                add_new_user_log(request.remote_addr, userdata["email"], False)
                return "success"
            else:
                add_new_user_log(request.remote_addr, userdata["email"], True)
                #If the new user failed to be created, the user probably already exists so return the string "userexists" to signup.js
                return "userexists"
        except Exception as e:
            add_new_user_log(request.remote_addr, userdata["email"], True)
            add_error_log(request.remote_addr, log_get_user(), "New user insertion fail", e)
            return "servererror"
    #This is the signup validation page. It attempts to create the new user and, if is successful, it redirects the user to the login page.

#Account Page
@app.route('/users/account/')
def user_account():
    if current_user.is_authenticated:
        add_access_log(request.remote_addr, log_get_user(), "/users/account/ (user_account)", False, False)
        if link_check_exists(current_user.id, False):
            user_submission = get_patient(link_get(current_user.id)["patient_id"])
            #If the user is linked to any patient data, get that data to be displayed on their account page.
        else:
            user_submission = None
        return render_template('/users/account.html', page_name=current_user.username, userdata=user_get_single(current_user.id), user_submission=user_submission)
    else:
        add_access_log(request.remote_addr, log_get_user(), "/users/account/ (user_account)", True, False)
        return redirect('/')
    #This is the user's account page. It shows their information along with any patient data they are linked to.
    #It also allows them to modify and delete their data and modify and delete their account.
    
#Modify
@app.route('/users/account/modify/')
def user_modify():
    if current_user.is_authenticated:
        add_access_log(request.remote_addr, log_get_user(), "/users/account/modify/ (user_modify)", False, False)
        return render_template('/users/modify.html', page_name="Modify Account", userdata=user_get_single(current_user.id))
    else:
        add_access_log(request.remote_addr, log_get_user(), "/users/account/modify/ (user_modify)", True, False)
        return redirect('/')
    #This is the user modification page. It looks like the signup page, but all the inputs will contain the user's information apart from the password box.
    #This page allows the user to modify their account details.
@app.route('/users/account/modify/validate/', methods=['POST'])
def user_modify_validate():
    if current_user.is_authenticated:
        userdata = request.get_data() #Get the data, decode it and make it a dictionary as in the previous routes.
        userdata = userdata.decode()
        userdata = ast.literal_eval(userdata)
        userdata["id"] = current_user.id
        add_access_log(request.remote_addr, log_get_user(), "/users/account/modify/validate/ (user_modify_validate)", False, False)
        try:
            if user_update(userdata) is True: #Try to update the user's information
                add_modify_user_log(request.remote_addr, userdata["email"], False)
                return "success"
            else:
                add_modify_user_log(request.remote_addr, userdata["email"], True)
                return "userexists"
        except Exception as e:
            add_modify_user_log(request.remote_addr, userdata["email"], True)
            add_error_log(request.remote_addr, log_get_user(), "User modify error", e)
            return "servererror"
    else:
        add_access_log(request.remote_addr, log_get_user(), "/users/account/modify/validate/ (user_modify_validate)", False, False)
        return abort(404)
    #This is the user modification validation page. It takes the modified user data the user submitted and attempts to modify their account with the data.
    
@app.route('/users/account/submission/modify/')
def user_submission_modify():
    if current_user.is_authenticated:
        if link_check_exists(current_user.id, False): #Check that a link exists. Without the link, there is no data to modify.
            add_access_log(request.remote_addr, log_get_user(), "/users/account/submission/modify/ (user_submission_modify)", False, False)
            patient_data = get_patient(link_get(current_user.id)["patient_id"]) #Get the patient data using the user's link to it.
            return render_template('modify_submission.html', page_name="Modify Submission", patient_data=patient_data)
        else:
            add_access_log(request.remote_addr, log_get_user(), "/users/account/submission/modify/ (user_submission_modify)", True, False)
            return redirect('/users/account/')
    else:
        add_access_log(request.remote_addr, log_get_user(), "/users/account/submission/modify/ (user_submission_modify)", True, False)
        return redirect('/users/login/')
    #This is the patient data modification page. It allows the user to modify their submission and resubmit it.
@app.route('/users/account/submission/modify/validate/', methods=['POST'])
def user_submission_modify_validate():
    if current_user.is_authenticated:
        subdata = request.get_data()
        subdata = subdata.decode()
        subdata = ast.literal_eval(subdata)
        add_access_log(request.remote_addr, log_get_user(), "/users/account/submission/modify/validate/' (user_submission_modify_validate)", False, False)
        if link_check_exists(current_user.id, False): #Make sure the link still exists.
            is_mongodb = False
            patient_id = link_get(current_user.id)["patient_id"] #Get the patient data's ID user the user's link to it.
            try:
                clean_subdata(subdata) #Clean the submitted data.
                update_patient(subdata, patient_id) #Update the patient data in MySQL with the new data.
                add_modify_patient_log(request.remote_addr, log_get_user(), False, is_mongodb, patient_id)
                is_mongodb = True
                mongo_update({"MySQL_ID": int(patient_id)}, subdata, m_client) #Modify the patient data in MongoDB with the new data.
                add_modify_patient_log(request.remote_addr, log_get_user(), False, is_mongodb, patient_id)
                return "success"
            except Exception as e:
                add_modify_patient_log(request.remote_addr, log_get_user(), True, is_mongodb, patient_id)
                add_error_log(request.remote_addr, log_get_user(), "Failed to modify user submission", e)
                return "servererror"
        else:
            add_error_log(request.remote_addr, log_get_user(), "Failed to modify user submission, user has no link to any patient data", None)
            return "nolink"
    else:
        add_access_log(request.remote_addr, log_get_user(), "/users/account/submission/modify/validate/' (user_submission_modify_validate)", True, False)
        return redirect('/users/login/')
    #This is the patient data modification validation page. It takes the resubmitted patient data and modifies the selected patient with said data.
    
@app.route('/users/account/submission/delete/')
def delete_submissionconfirm():
    if current_user.is_authenticated:
        add_access_log(request.remote_addr, log_get_user(), "/users/account/submission_delete/ (delete_submissionconfirm)", False, False)
        return render_template('delete_submission.html', page_name="Delete Submission Confirmation")
    else:
        add_access_log(request.remote_addr, log_get_user(), "/users/accout/submission_delete/ (delete_submissionconfirm)", True, False)
        abort(404)
    #This is the submission deletion page. It asks the user if they are sure if they want to delete their submission or not.
@app.route('/users/account/submission/delete/confirmed/')
def delete_submission_confirmed():
    if current_user.is_authenticated:
        if link_check_exists(current_user.id, False):
            add_access_log(request.remote_addr, log_get_user(), "/users/account/submission_delete/confirmed/ (delete_submission_confirmed)", False, False)
            patient_id = link_get(current_user.id)["patient_id"]
            admin_delete_patient_data(patient_id) #Delete the patient data from MySQL using the patient ID.
            add_delete_db_log(request.remote_addr, log_get_user(), False, patient_id, False) #Add a log to show the data has been deleted.
            mongo_delete({"MySQL_ID": int(patient_id)}, m_client) #Delete the patient data from MongoDB using the patient ID.
            add_delete_db_log(request.remote_addr, log_get_user(), False, patient_id, False)
            return redirect('/users/account/')
        else:
            add_access_log(request.remote_addr, log_get_user(), "/users/account/submission_delete/confirmed/ (delete_submission_confirmed)", True, False)
            return redirect('/users/account/')
    else:
        add_access_log(request.remote_addr, log_get_user(), "/users/account/submission_delete/confirmed/ (delete_submission_confirmed)", True, False)
        abort(404)
    #This is the submission deletion confirmed page. The user has confirmed their intent to delete their submission and thus their submission is deleted.
    
#Delete
@app.route('/users/account/delete/')
def user_deleteconfirm():
    if current_user.is_authenticated:
        add_access_log(request.remote_addr, log_get_user(), "/users/account/delete/ (user_deleteconfirm)", False, False)
        return render_template('/users/delete.html', page_name="Delete Confirmation")
    else:
        add_access_log(request.remote_addr, log_get_user(), "/users/account/delete/ (user_deleteconfirm)", True, False)
        abort(404)
    #This is the account deletion page. It asks the user if they are sure they want to delete their account or not.
@app.route('/users/account/delete/confirmed/')
def user_delete():
    if current_user.is_authenticated:
        add_access_log(request.remote_addr, log_get_user(), "/users/account/delete/confirmed/ (user_delete)", False, False)
        temp_user_id = current_user.id
        add_login_log(request.remote_addr, log_get_user(), False, True)
        logout_user() #Before deleting the user, log them out.
        add_delete_user_log(request.remote_addr, log_get_user(), False, False) #Add a user deleted log.
        admin_delete_user(temp_user_id) #Delete the user.
        return redirect('/')
    else:
        add_access_log(request.remote_addr, log_get_user(), "/users/account/delete/confirmed/ (user_delete)", True, False)
        abort(404)
    #This is the account deletion confirmed page. The user has confirmed that they want to delete their account and thus their account is deleted
    #along with any links they have to patient data.
    
#Logout
@app.route('/users/logout/')
def user_logout():
    if current_user.is_authenticated:
        add_access_log(request.remote_addr, log_get_user(), "/users/logout/ (user_logout)", False, False)
        add_login_log(request.remote_addr, log_get_user(), False, True) #Add a log to show that the user has logged out.
        logout_user() #Log the user out.
        return redirect('/')
    else:
        add_access_log(request.remote_addr, log_get_user(), "/users/logout/ (user_logout)", True, False)
        return redirect('/')
    #This is the logout page. It... Logs the user out... Kind of obvious really.

#This is the start of the admin routes. They allow control over a lot of the website so normal users should not have access.SS
'''Admin Routes'''
#Main
@app.route('/admin/')
def admin_main():
    if current_user.is_authenticated:
        if current_user.is_admin is True: #Make sure the user is an admin before allowing access to this page.
            add_access_log(request.remote_addr, log_get_user(), "/admin/ (admin_main)", False, True)
            return render_template('/admin/admin_main.html', page_name="Admin: Home")
        else:
            add_access_log(request.remote_addr, log_get_user(), "/admin/ (admin_main)", True, True)
            abort(404) #If the user is not an admin, show a 404 page.
    else:
        add_access_log(request.remote_addr, log_get_user(), "/admin/ (admin_main)", True, True)
        abort(404)
        #If the user is not logged in, they can't be an admin either, so show a 404 page.
    #This is the main admin page. It shows three options: User Management, Patient Management and Database Management.
    #The reason for showing a 404 page not found error rather than a 403 forbidden page is for security.
    #With a 403, the user knows the page exists, but they don't have access.
    #With 404, the user thinks the page doesn't exist so they don't know admin pages exist.
    
#User Management
@app.route('/admin/users/')
def admin_user_management():
    if current_user.is_authenticated:
        if current_user.is_admin is True:
            add_access_log(request.remote_addr, log_get_user(), "/admin/users/ (admin_user_management)", False, True)
            return render_template('/admin/admin_user_management.html', page_name="Admin: User Management", userdata=user_get_all())
        else:
            add_access_log(request.remote_addr, log_get_user(), "/admin/users/ (admin_user_management)", True, True)
            abort(404)
    else:
        add_access_log(request.remote_addr, log_get_user(), "/admin/users/ (admin_user_management)", True, True)
        abort(404)
    #The user management page. It shows all the users that exist in the database and gives the option to delete them or make them admins. (Or revoke their admin access)
#Change Admin Status
#This route allows the website to store variables in the URL for the route to use. In this case, that variable is the user_id we want to change the admin status of.
@app.route('/admin/users/makeadmin/user_id=<user_id>')
def admin_user_apply_admin(user_id):
    if current_user.is_authenticated:
        if current_user.is_admin is True:
            add_access_log(request.remote_addr, log_get_user(), "/admin/users/makeadmin/user_id=" + str(user_id) + " (admin_user_apply_admin)", False, True)
            if admin_apply_admin_user(user_id) is True: #Makes the selected user an admin.
                add_user_admin_log(request.remote_addr, user_get_username(user_id), False, False)
                #Adds an admin change log to show that a user's admin status has been changed.
            else:
                add_user_admin_log(request.remote_addr, user_get_username(user_id), False, True)
            return redirect('/admin/users/')
        else:
            add_access_log(request.remote_addr, log_get_user(), "/admin/users/makeadmin/user_id=" + str(user_id) + " (admin_user_apply_admin)", True, True)
            abort(404)
    else:
        add_access_log(request.remote_addr, log_get_user(), "/admin/users/makeadmin/user_id=" + str(user_id) + " (admin_user_apply_admin)", True, True)
        abort(404)
    #This route simply changes the admin status of the selected user.
#Delete
@app.route('/admin/users/delete/user_id=<user_id>')
def admin_user_delete(user_id):
    if current_user.is_authenticated:
        if current_user.is_admin is True:
            add_access_log(request.remote_addr, log_get_user(), "/admin/users/delete/user_id=" + str(user_id) + " (admin_user_delete)", False, True)
            if int(user_id) == current_user.id: #If the user deleting the selected user are one and the same:
                user = user_get_username(user_id)
                logout_user() #Logout the user being deleted if they are the one deleting their account.
                add_login_log(request.remote_addr, user, False, True)
                add_delete_user_log(request.remote_addr, user, False, True) #Add a user deletion log and show that it was deleted by an admin.
                admin_delete_user(user_id) #Delete the selected user.
                return redirect('/')
            else: #The user and deleting user are not the same.
                add_delete_user_log(request.remote_addr, user_get_username(user_id), False, True) #Add a user deletion log and show that it was deleted by an admin.
                admin_delete_user(user_id) #Delete the user.
                return redirect('/admin/users/')
        else:
            add_access_log(request.remote_addr, log_get_user(), "/admin/users/delete/user_id=" + str(user_id) + " (admin_user_delete)", True, True)
            abort(404)
    else:
        add_access_log(request.remote_addr, log_get_user(), "/admin/users/delete/user_id=" + str(user_id) + " (admin_user_delete)", True, True)
        abort(404)
    #This page allows admins to deleted selected users. If the admin is deleting their own account, it logs them out first like with normal user deletion.

#Patient Data Management
@app.route('/admin/database/manage/')
def admin_database_management():
    if current_user.is_authenticated:
        if current_user.is_admin:
            add_access_log(request.remote_addr, log_get_user(), "/admin/database/manage/ (admin_database_management)", False, True)
            patient_data = admin_get_patient_data() #Get the patient data from MySQL
            links = link_get_all() #Get the links from MySQL.
            if links is not None and len(links) >= 1: #If their are any links, add each one to its corresponding patient dictionary in patient_data.
                for link in links:
                    for patient in patient_data:
                        if patient["id"] == link["patient_id"]:
                            patient["user_link"] = link["user_name"]
            return render_template('/admin/admin_patient_management.html', page_name="Admin: Patient Data Management (MySQL)", patient_data=patient_data, is_mongodb=False)
        else:
            add_access_log(request.remote_addr, log_get_user(), "/admin/database/manage/ (admin_database_management)", True, True)
            abort(404)
    else:
        add_access_log(request.remote_addr, log_get_user(), "/admin/database/manage/ (admin_database_management)", True, True)
        abort(404)
    #This is the admin patient data page. It allows admins to see all the patient data in the database and delelte it if they want.
    #This page is specifically for showing the MySQL data.
@app.route('/admin/database/manage/mongodb/')
def admin_database_management_mongodb():
    if current_user.is_authenticated:
        if current_user.is_admin:
            add_access_log(request.remote_addr, log_get_user(), "/admin/database/manage/mongodb/ (admin_database_management_mongodb)", False, True)
            return render_template('/admin/admin_patient_management.html', page_name="Admin: Patient Data Management (MongoDB)", patient_data=mongo_find_all(True, m_client), is_mongodb=True)
        else:
            add_access_log(request.remote_addr, log_get_user(), "/admin/database/manage/ (admin_database_management)", True, True)
            abort(404)
    else:
        add_access_log(request.remote_addr, log_get_user(), "/admin/database/manage/ (admin_database_management)", True, True)
        abort(404)
    #This is the same page as '/admin/database/manage/', but it shows the MongoDB data instead.

#Delete Data
@app.route('/admin/database/delete/patient_id=<patient_id>')
def admin_database_delete(patient_id):
    if current_user.is_authenticated:
        if current_user.is_admin:
            add_access_log(request.remote_addr, log_get_user(), "/admin/database/delete/patient_id=" + str(patient_id) + " (admin_database_delete)", False, True)
            admin_delete_patient_data(patient_id) #Delete the selected data from the MySQL database.
            add_delete_db_log(request.remote_addr, log_get_user(), False, patient_id, True) #Add a deleted data log and show that it was deleted by an admin.
            mongo_delete({"MySQL_ID": int(patient_id)}, m_client) #Delete the selected data from the MongoDB database.
            add_delete_db_log(request.remote_addr, log_get_user(), True, patient_id, True) #Add a deleted data log and show that it was deleted by an admin.
            return redirect('/admin/database/manage/')
        else:
            add_access_log(request.remote_addr, log_get_user(), "/admin/database/delete/patient_id=" + str(patient_id) + " (admin_database_delete)", True, True)
            abort(404)
    else:
        add_access_log(request.remote_addr, log_get_user(), "/admin/database/delete/patient_id=" + str(patient_id) + " (admin_database_delete)", True, True)
        abort(404)
    #This page is the admin patient data deletion page. It allows admins to delete the selected patient data from both the MySQL database and MongoDB database.

#Database Management
@app.route('/admin/all_databases/manage/')
def admin_aDB_manage():
    if current_user.is_authenticated:
        if current_user.is_admin:
            add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/ (admin_aDB_manage)", False, True)
            return render_template('/admin/admin_database_management.html', page_name="Admin: Database Management")
        else:
            add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/ (admin_aDB_manage)", True, True)
            abort(404)
    else:
        add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/ (admin_aDB_manage)", True, True)
        abort(404)
    #This is the database management page. It shows the user several options with those options being:
    #Duamp All Data
    #Delete All Users
    #Delete All Patient Data
    #Delete All Links
    #Delete ALL DATA

#Delete All Users        
@app.route('/admin/all_databases/manage/delete_users/')
def admin_aDB_delete_users():
    if current_user.is_authenticated:
        if current_user.is_admin:
            add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/delete_users/ (admin_aDB_delete_users)", False, True)
            return render_template('/admin/confirmation.html', page_name="Admin: Delete All Users", dir_to_use="admin_aDB_delete_users_confirmed", message="Are you sure you want to delete ALL users?:", yes_message="Delete All Users", no_message="Keep All Users")
        else:
            add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/delete_users/ (admin_aDB_delete_users)", True, True)
            abort(404)
    else:
        add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/delete_users/ (admin_aDB_delete_users)", True, True)
        abort(404)
    #This page asks the admin if they are sure they want to delete all users or not.
@app.route('/admin/all_databases/manage/delete_users/confirmed/')
def admin_aDB_delete_users_confirmed():
    if current_user.is_authenticated:
        if current_user.is_admin:
            add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/delete_users/confirmed/ (admin_aDB_delete_users_confirmed)", False, True)
            user = current_user.username
            if current_user.username != "BaseAdmin": #If the current user is not the BaseAdmin, they need to be logged out as their account will be deleted.
                logout_user()
            admin_user_nuke() #Delete ALL user data.
            add_admin_nuke_log(request.remote_addr, user, "table_users", False) #Log the extreme data management.
            return redirect('/')
        else:
            add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/delete_users/confirmed/ (admin_aDB_delete_users_confirmed)", True, True)
            abort(404)
    else:
        add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/delete_users/confirmed/ (admin_aDB_delete_users_confirmed)", True, True)
        abort(404)
    #This is the user 'nuke' page. The admin has confirmed they

#Delete All Patients        
@app.route('/admin/all_databases/manage/delete_patients/')
def admin_aDB_delete_patients():
    if current_user.is_authenticated:
        if current_user.is_admin:
            add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/delete_patients/ (admin_aDB_delete_patients)", False, True)
            return render_template('/admin/confirmation.html', page_name="Admin: Delete All Patient Data", dir_to_use="admin_aDB_delete_patients_confirmed", message="Are you sure you want to delete ALL patient data? (Refer to terminal for progress):", yes_message="Delete All Patient Data", no_message="Keep All Patient Data")
        else:
            add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/delete_patients/ (admin_aDB_delete_patients)", True, True)
            abort(404)
    else:
        add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/delete_patients/ (admin_aDB_delete_patients)", True, True)
        abort(404)
    #This page asks the admin if they are sure they want to delete all patients or not.
@app.route('/admin/all_databases/manage/delete_patients/confirmed/')
def admin_aDB_delete_patients_confirmed():
    if current_user.is_authenticated:
        if current_user.is_admin:
            add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/delete_patients/confirmed/ (admin_aDB_delete_patients_confirmed)", False, True)
            admin_patient_nuke() #Delete all patient data from MySQL
            mongo_nuke(m_client) #Delete all patient data from MongoDB
            add_admin_nuke_log(request.remote_addr, log_get_user(), "table_patient_data", False)
            return redirect('/admin/all_databases/manage/')
        else:
            add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/delete_patients/confirmed/ (admin_aDB_delete_patients_confirmed)", True, True)
            abort(404)
    else:
        add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/delete_patients/confirmed/ (admin_aDB_delete_patients_confirmed)", True, True)
        abort(404)
    #This page delete all patient data from MySQL and MongoDB

#Delete All Links        
@app.route('/admin/all_databases/manage/delete_links/')
def admin_aDB_delete_links():
    if current_user.is_authenticated:
        if current_user.is_admin:
            add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/delete_links/ (admin_aDB_delete_links)", False, True)
            return render_template('/admin/confirmation.html', page_name="Admin: Delete All Patient Data", dir_to_use="admin_aDB_delete_links_confirmed", message="Are you sure you want to delete ALL links between users and patient data?:", yes_message="Delete All Links", no_message="Keep All Links")
        else:
            add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/delete_links/ (admin_aDB_delete_links)", True, True)
            abort(404)
    else:
        add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/delete_links/ (admin_aDB_delete_links)", True, True)
        abort(404)
    #This page asks the admin if they are sure they want to delete all links or not.
@app.route('/admin/all_databases/manage/delete_links/confirmed/')
def admin_aDB_delete_links_confirmed():
    if current_user.is_authenticated:
        if current_user.is_admin:
            add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/delete_links/confirmed/ (admin_aDB_delete_links_confirmed)", False, True)
            admin_link_nuke() #Deletes all links in MySQL.
            add_admin_nuke_log(request.remote_addr, log_get_user(), "link_user_patient_data", False)
            return redirect('/admin/all_databases/manage/')
        else:
            add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/delete_links/confirmed/ (admin_aDB_delete_links_confirmed)", True, True)
            abort(404)
    else:
        add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/delete_links/confirmed/ (admin_aDB_delete_links_confirmed)", True, True)
        abort(404)
    #This page deletes all links from MySQL.

#Delete EVERYTHING        
@app.route('/admin/all_databases/manage/delete_nuke_all/')
def admin_aDB_delete_nuke_all():
    if current_user.is_authenticated:
        if current_user.is_admin:
            add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/delete_nuke_all/ (admin_aDB_delete_nuke_all)", False, True)
            return render_template('/admin/confirmation.html', page_name="Admin: Delete All Patient Data", dir_to_use="admin_aDB_delete_nuke_all_confirmed", message="Are you sure you want to delete ALL DATA?!:", yes_message="Delete All Data", no_message="Keep All Data")
        else:
            add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/delete_nuke_all/ (admin_aDB_delete_nuke_all)", True, True)
            abort(404)
    else:
        add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/delete_nuke_all/ (admin_aDB_delete_nuke_all)", True, True)
        abort(404)
    #This page asks the admin if they are sure they want to delete ALL DATA from ALL tables or not.
@app.route('/admin/all_databases/manage/delete_nuke_all/confirmed/')
def admin_aDB_delete_nuke_all_confirmed():
    if current_user.is_authenticated:
        if current_user.is_admin:
            add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/delete_nuke_all/confirmed/ (admin_aDB_delete_nuke_all_confirmed)", False, True)
            user = current_user.username
            if current_user.username != "BaseAdmin":
                logout_user()
            admin_nuke(m_client)
            add_admin_nuke_log(request.remote_addr, user, "EVERYTHING!", True) #Add an admin nuke log and show that EVERYTHING was deleted with True.
            return redirect('/')
        else:
            add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/delete_nuke_all/confirmed/ (admin_aDB_delete_nuke_all_confirmed)", True, True)
            abort(404)
    else:
        add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/delete_nuke_all/confirmed/ (admin_aDB_delete_nuke_all_confirmed)", True, True)
        abort(404)
    #This page deletes all data from all tables in both MySQL and MongoDB.

@app.route('/admin/all_databases/manage/dump/')
def admin_aDB_dump():
    if current_user.is_authenticated:
        if current_user.is_admin:
            add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/dump/ (admin_aDB_dump)", False, True)
            admin_dump_data() #Dump all data into dumps files.
            add_admin_dump_log(request.remote_addr, log_get_user()) #Add a log to show that data was dumped.
            return redirect('/admin/all_databases/manage/')
        else:
            add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/dump/ (admin_aDB_dump)", True, True)
            abort(404)
    else:
        add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/dump/ (admin_aDB_dump)", True, True)
        abort(404)
    #This page dumps all data from all tables into three text files in '/static/dumps/'

#DB Loader
@app.route('/admin/database/manage/load_db/')
def admin_loadDB():
    if current_user.is_authenticated:
        if current_user.is_admin is True:
            add_access_log(request.remote_addr, log_get_user(), "/admin/load_db/ (admin_loadDB)", False, True)
            from db_reader import read_presaved_data
            read_presaved_data(True, True, m_client) #Read the data from 'healthcare-dataset-stroke-data.csv' into MySQL and MongoDB
            add_readDB_admin_log(request.remote_addr, log_get_user())
            return redirect('/admin/database/manage/')
        else:
            add_access_log(request.remote_addr, log_get_user(), "/admin/load_db/ (admin_loadDB)", True, True)
            abort(404)
    else:
        add_access_log(request.remote_addr, log_get_user(), "/admin/load_db/ (admin_loadDB)", True, True)
        abort(404)
    #This page loads data from 'healthcare-dataset-stroke-data.csv' into the databases. Because of the size of this file, this takes a few minutes during which
    #the website is unresponsive. However, in the console/terminal, progress is shown. There is around 5111 entries in this file.

#Error Pages
#These pages are only shown when the website encounters an error.
#404 is page not found.
@app.errorhandler(404)
def page_invalid(e):
    add_access_log(request.remote_addr, log_get_user(), "/404/ (page_invalid)", False, False)
    return render_template('errors/404.html'), 404
@app.errorhandler(405)
def page_wrong_method(e):
    add_access_log(request.remote_addr, log_get_user(), "/405/ (page_wrong_method)", False, False)
    abort(404)
#For simplicity, if the website encounters a 405 error, it will redirect and show as a 404 instead.

#Favicon
#Apparently supposed to be the icon used when a page is bookmarked.
#Even though this supresses the "favicon.ico" 404 error, it does not show this icon when bookmarked.
@app.route('/favicon.ico')
def favicon():
    add_access_log(request.remote_addr, log_get_user(), "/favicon.ico (favicon)", False, False)
    return url_for("static", filename="favicon.ico")

#Launch Website
if __name__ == '__main__':
    if deployed is True:
        from waitress import serve
        serve(app, host="0.0.0.0", port=5000)
    else:
        app.run(host="0.0.0.0", debug=True)
    #Here the website is run.
    #If deployed is True, it will run on a more secure server using the waitress library.
    #If deployed is False, it will run on a debug server which is insecure.
    #In both cases, the website is run on the localhost on port 5000.
    #With the host being set to "0.0.0.0" in both cases, any devices on the local network can access the website.
    #It is not accessable to the internet without port forwarding.