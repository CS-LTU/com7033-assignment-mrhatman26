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
m_client = pymongo.MongoClient("mongodb://localhost:27017") #Open a socket connection to the mongodb database.
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
    if current_user.is_authenticated:
        add_access_log(request.remote_addr, log_get_user(), "/submission/ (submission)", False, False)
        return render_template('submission.html', page_name="Submission", already_submitted=link_check_exists(current_user.id, False))
    else:
        add_access_log(request.remote_addr, log_get_user(), "/submission/ (submission)", True, False)
        return redirect('/users/login/')
@app.route('/submission/validate/', methods=['POST'])
def submission_validate():
    if current_user.is_authenticated:
        subdata = request.get_data()
        subdata = subdata.decode()
        subdata = ast.literal_eval(subdata)
        add_access_log(request.remote_addr, log_get_user(), "/submission/validate/ (submission_validate)", False, False)
        mysql_done = False
        try:
            clean_subdata(subdata)
            mysql_id = insert_new_patient_link(subdata, current_user.id)
            subdata["MySQL_ID"] = mysql_id
            mysql_done = True
            add_new_patient_log(request.remote_addr, log_get_user(), False, False)
            mongo_insert(subdata, m_client)
            add_new_patient_log(request.remote_addr, log_get_user(), False, True)
            return "success"
        except Exception as e:
            add_new_patient_log(request.remote_addr, log_get_user(), True, mysql_done)
            add_error_log(request.remote_addr, log_get_user(), "Submission data insertion failed.", e)
            return "servererror"
    else:
        add_access_log(request.remote_addr, log_get_user(), "/submission/validate/ (submission_validate)", True, False)
        return redirect('/users/login/')
    
@app.route('/data/view/')
def view_data():
    if current_user.is_authenticated:
        add_access_log(request.remote_addr, log_get_user(), "/data/view/ (view_data)", False, False)
        return render_template('data.html', page_name="Submitted Data", patient_data=mongo_find_all(False, m_client))
    else:
        add_access_log(request.remote_addr, log_get_user(), "/data/view/ (view_data)", True, False)
        return redirect('/users/login/')
    
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
@app.route('/users/login/validate/', methods=['POST'])
def user_login_validate():
    if current_user.is_authenticated:
        add_access_log(request.remote_addr, log_get_user(), "/users/login/validate/ (user_login_validate)", True, False)
        return redirect('/')
    else:
        userdata = request.get_data()
        userdata = userdata.decode()
        userdata = ast.literal_eval(userdata)
        add_access_log(request.remote_addr, log_get_user(), "/users/login/validate/ (user_login_validate)", False, False)
        try:
            if user_check_validate(userdata) is True:
                login_user(User(user_get_id(userdata["username"]), userdata["username"], admin_user_admin_check(userdata["username"])))
                add_login_log(request.remote_addr, userdata["username"], False, False)
                return "success"
            else:
                add_login_log(request.remote_addr, userdata["username"], True, False)
                return "usernotexist"
        except Exception as e:
            add_login_log(request.remote_addr, userdata["username"], True, False)
            add_error_log(request.remote_addr, log_get_user(), "Login user fail", e)
            return "servererror"

#Signup
@app.route('/users/signup/')
def user_signup():
    if current_user.is_authenticated:
        add_access_log(request.remote_addr, log_get_user(), "/users/signup/ (user_signup)", True, False)
        return redirect('/')
    else:
        add_access_log(request.remote_addr, log_get_user(), "/users/signup/ (user_signup)", False, False)
        return render_template('users/signup.html', page_name="Signup")
@app.route('/users/signup/validate/', methods=['POST'])
def user_signup_validate():
    if current_user.is_authenticated:
        add_access_log(request.remote_addr, log_get_user(), "/users/signup/validate/ (user_signup_validate)", True, False)
        return redirect('/')
    else:
        userdata = request.get_data()
        userdata = userdata.decode()
        userdata = ast.literal_eval(userdata)
        add_access_log(request.remote_addr, log_get_user(), "/users/signup/validate/ (user_signup_validate)", False, False)
        try:
            if user_create(userdata) is True:
                add_new_user_log(request.remote_addr, userdata["email"], False)
                return "success"
            else:
                add_new_user_log(request.remote_addr, userdata["email"], True)
                return "userexists"
        except Exception as e:
            add_new_user_log(request.remote_addr, userdata["email"], True)
            add_error_log(request.remote_addr, log_get_user(), "New user insertion fail", e)
            return "servererror"
        
#Account Page
@app.route('/users/account/')
def user_account():
    if current_user.is_authenticated:
        add_access_log(request.remote_addr, log_get_user(), "/users/account/ (user_account)", False, False)
        if link_check_exists(current_user.id, False):
            user_submission = get_patient(link_get(current_user.id)["patient_id"])
        else:
            user_submission = None
        return render_template('/users/account.html', page_name=current_user.username, userdata=user_get_single(current_user.id), user_submission=user_submission)
    else:
        add_access_log(request.remote_addr, log_get_user(), "/users/account/ (user_account)", True, False)
        return redirect('/')
    
#Modify
@app.route('/users/account/modify/')
def user_modify():
    if current_user.is_authenticated:
        add_access_log(request.remote_addr, log_get_user(), "/users/account/modify/ (user_modify)", False, False)
        return render_template('/users/modify.html', page_name="Modify Account", userdata=user_get_single(current_user.id))
    else:
        add_access_log(request.remote_addr, log_get_user(), "/users/account/modify/ (user_modify)", True, False)
        return redirect('/')
@app.route('/users/account/modify/validate/', methods=['POST'])
def user_modify_validate():
    if current_user.is_authenticated:
        userdata = request.get_data()
        userdata = userdata.decode()
        userdata = ast.literal_eval(userdata)
        userdata["id"] = current_user.id
        add_access_log(request.remote_addr, log_get_user(), "/users/account/modify/validate/ (user_modify_validate)", False, False)
        try:
            if user_update(userdata) is True:
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
    
@app.route('/users/account/submission/modify/')
def user_submission_modify():
    if current_user.is_authenticated:
        if link_check_exists(current_user.id, False):
            add_access_log(request.remote_addr, log_get_user(), "/users/account/submission/modify/ (user_submission_modify)", False, False)
            patient_data = get_patient(link_get(current_user.id)["patient_id"])
            return render_template('modify_submission.html', page_name="Modify Submission", patient_data=patient_data)
        else:
            add_access_log(request.remote_addr, log_get_user(), "/users/account/submission/modify/ (user_submission_modify)", True, False)
            return redirect('/users/account/')
    else:
        add_access_log(request.remote_addr, log_get_user(), "/users/account/submission/modify/ (user_submission_modify)", True, False)
        return redirect('/users/login/')
@app.route('/users/account/submission/modify/validate/', methods=['POST'])
def user_submission_modify_validate():
    if current_user.is_authenticated:
        subdata = request.get_data()
        subdata = subdata.decode()
        subdata = ast.literal_eval(subdata)
        add_access_log(request.remote_addr, log_get_user(), "/users/account/submission/modify/validate/' (user_submission_modify_validate)", False, False)
        if link_check_exists(current_user.id, False):
            is_mongodb = False
            patient_id = link_get(current_user.id)["patient_id"]
            try:
                clean_subdata(subdata)
                update_patient(subdata, patient_id)
                add_modify_patient_log(request.remote_addr, log_get_user(), False, is_mongodb, patient_id)
                is_mongodb = True
                mongo_update({"MySQL_ID": int(patient_id)}, subdata, m_client)
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

    
@app.route('/users/account/submission/delete/')
def delete_submissionconfirm():
    if current_user.is_authenticated:
        add_access_log(request.remote_addr, log_get_user(), "/users/account/submission_delete/ (delete_submissionconfirm)", False, False)
        return render_template('delete_submission.html', page_name="Delete Submission Confirmation")
    else:
        add_access_log(request.remote_addr, log_get_user(), "/users/accout/submission_delete/ (delete_submissionconfirm)", True, False)
        abort(404)
@app.route('/users/account/submission/delete/confirmed/')
def delete_submission_confirmed():
    if current_user.is_authenticated:
        if link_check_exists(current_user.id, False):
            add_access_log(request.remote_addr, log_get_user(), "/users/account/submission_delete/confirmed/ (delete_submission_confirmed)", False, False)
            patient_id = link_get(current_user.id)["patient_id"]
            admin_delete_patient_data(patient_id)
            add_delete_db_log(request.remote_addr, log_get_user(), False, patient_id, False)
            mongo_delete({"MySQL_ID": int(patient_id)}, m_client)
            add_delete_db_log(request.remote_addr, log_get_user(), False, patient_id, False)
            return redirect('/users/account/')
        else:
            add_access_log(request.remote_addr, log_get_user(), "/users/account/submission_delete/confirmed/ (delete_submission_confirmed)", True, False)
            return redirect('/users/account/')
    else:
        add_access_log(request.remote_addr, log_get_user(), "/users/account/submission_delete/confirmed/ (delete_submission_confirmed)", True, False)
        abort(404)
    
#Delete
@app.route('/users/account/delete/')
def user_deleteconfirm():
    if current_user.is_authenticated:
        add_access_log(request.remote_addr, log_get_user(), "/users/account/delete/ (user_deleteconfirm)", False, False)
        return render_template('/users/delete.html', page_name="Delete Confirmation")
    else:
        add_access_log(request.remote_addr, log_get_user(), "/users/account/delete/ (user_deleteconfirm)", True, False)
        abort(404)
@app.route('/users/account/delete/confirmed/')
def user_delete():
    if current_user.is_authenticated:
        add_access_log(request.remote_addr, log_get_user(), "/users/account/delete/confirmed/ (user_delete)", False, False)
        temp_user_id = current_user.id
        add_login_log(request.remote_addr, log_get_user(), False, True)
        logout_user()
        add_delete_user_log(request.remote_addr, log_get_user(), False, False)
        admin_delete_user(temp_user_id)
        return redirect('/')
    else:
        add_access_log(request.remote_addr, log_get_user(), "/users/account/delete/confirmed/ (user_delete)", True, False)
        abort(404)
    
#Logout
@app.route('/users/logout/')
def user_logout():
    if current_user.is_authenticated:
        add_access_log(request.remote_addr, log_get_user(), "/users/logout/ (user_logout)", False, False)
        add_login_log(request.remote_addr, log_get_user(), False, True)
        logout_user()
        return redirect('/')
    else:
        add_access_log(request.remote_addr, log_get_user(), "/users/logout/ (user_logout)", True, False)
        return redirect('/')

'''Admin Routes'''
#Main
@app.route('/admin/')
def admin_main():
    if current_user.is_authenticated:
        if current_user.is_admin is True:
            add_access_log(request.remote_addr, log_get_user(), "/admin/ (admin_main)", False, True)
            return render_template('/admin/admin_main.html', page_name="Admin: Home")
        else:
            add_access_log(request.remote_addr, log_get_user(), "/admin/ (admin_main)", True, True)
            abort(404)
    else:
        add_access_log(request.remote_addr, log_get_user(), "/admin/ (admin_main)", True, True)
        abort(404)
    
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
#Change Admin Status
@app.route('/admin/users/makeadmin/user_id=<user_id>')
def admin_user_apply_admin(user_id):
    if current_user.is_authenticated:
        if current_user.is_admin is True:
            add_access_log(request.remote_addr, log_get_user(), "/admin/users/makeadmin/user_id=" + str(user_id) + " (admin_user_apply_admin)", False, True)
            if admin_apply_admin_user(user_id) is True:
                add_user_admin_log(request.remote_addr, user_get_username(user_id), False, False)
            else:
                add_user_admin_log(request.remote_addr, user_get_username(user_id), False, True)
            return redirect('/admin/users/')
        else:
            add_access_log(request.remote_addr, log_get_user(), "/admin/users/makeadmin/user_id=" + str(user_id) + " (admin_user_apply_admin)", True, True)
            abort(404)
    else:
        add_access_log(request.remote_addr, log_get_user(), "/admin/users/makeadmin/user_id=" + str(user_id) + " (admin_user_apply_admin)", True, True)
        abort(404)
#Delete
@app.route('/admin/users/delete/user_id=<user_id>')
def admin_user_delete(user_id):
    if current_user.is_authenticated:
        if current_user.is_admin is True:
            add_access_log(request.remote_addr, log_get_user(), "/admin/users/delete/user_id=" + str(user_id) + " (admin_user_delete)", False, True)
            if int(user_id) == current_user.id:
                user = user_get_username(user_id)
                logout_user()
                add_login_log(request.remote_addr, user, False, True)
                add_delete_user_log(request.remote_addr, user, False, True)
                admin_delete_user(user_id)
                return redirect('/')
            else:
                add_delete_user_log(request.remote_addr, user_get_username(user_id), False, True)
                admin_delete_user(user_id)
                return redirect('/admin/users/')
        else:
            add_access_log(request.remote_addr, log_get_user(), "/admin/users/delete/user_id=" + str(user_id) + " (admin_user_delete)", True, True)
            abort(404)
    else:
        add_access_log(request.remote_addr, log_get_user(), "/admin/users/delete/user_id=" + str(user_id) + " (admin_user_delete)", True, True)
        abort(404)

#Patient Data Management
@app.route('/admin/database/manage/')
def admin_database_management():
    if current_user.is_authenticated:
        if current_user.is_admin:
            add_access_log(request.remote_addr, log_get_user(), "/admin/database/manage/ (admin_database_management)", False, True)
            patient_data = admin_get_patient_data()
            links = link_get_all()
            if links is not None and len(links) >= 1:
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

#Delete Data
@app.route('/admin/database/delete/patient_id=<patient_id>')
def admin_database_delete(patient_id):
    if current_user.is_authenticated:
        if current_user.is_admin:
            add_access_log(request.remote_addr, log_get_user(), "/admin/database/delete/patient_id=" + str(patient_id) + " (admin_database_delete)", False, True)
            admin_delete_patient_data(patient_id)
            add_delete_db_log(request.remote_addr, log_get_user(), False, patient_id, True)
            mongo_delete({"MySQL_ID": int(patient_id)}, m_client)
            add_delete_db_log(request.remote_addr, log_get_user(), True, patient_id, True)
            return redirect('/admin/database/manage/')
        else:
            add_access_log(request.remote_addr, log_get_user(), "/admin/database/delete/patient_id=" + str(patient_id) + " (admin_database_delete)", True, True)
            abort(404)
    else:
        add_access_log(request.remote_addr, log_get_user(), "/admin/database/delete/patient_id=" + str(patient_id) + " (admin_database_delete)", True, True)
        abort(404)

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
@app.route('/admin/all_databases/manage/delete_users/confirmed/')
def admin_aDB_delete_users_confirmed():
    if current_user.is_authenticated:
        if current_user.is_admin:
            add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/delete_users/confirmed/ (admin_aDB_delete_users_confirmed)", False, True)
            user = current_user.username
            if current_user.username != "BaseAdmin":
                logout_user()
            admin_user_nuke()
            add_admin_nuke_log(request.remote_addr, user, "table_users", False)
            return redirect('/')
        else:
            add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/delete_users/confirmed/ (admin_aDB_delete_users_confirmed)", True, True)
            abort(404)
    else:
        add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/delete_users/confirmed/ (admin_aDB_delete_users_confirmed)", True, True)
        abort(404)

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
@app.route('/admin/all_databases/manage/delete_patients/confirmed/')
def admin_aDB_delete_patients_confirmed():
    if current_user.is_authenticated:
        if current_user.is_admin:
            add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/delete_patients/confirmed/ (admin_aDB_delete_patients_confirmed)", False, True)
            admin_patient_nuke()
            mongo_nuke(m_client)
            add_admin_nuke_log(request.remote_addr, log_get_user(), "table_patient_data", False)
            return redirect('/admin/all_databases/manage/')
        else:
            add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/delete_patients/confirmed/ (admin_aDB_delete_patients_confirmed)", True, True)
            abort(404)
    else:
        add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/delete_patients/confirmed/ (admin_aDB_delete_patients_confirmed)", True, True)
        abort(404)

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
@app.route('/admin/all_databases/manage/delete_links/confirmed/')
def admin_aDB_delete_links_confirmed():
    if current_user.is_authenticated:
        if current_user.is_admin:
            add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/delete_links/confirmed/ (admin_aDB_delete_links_confirmed)", False, True)
            admin_link_nuke()
            add_admin_nuke_log(request.remote_addr, log_get_user(), "link_user_patient_data", False)
            return redirect('/admin/all_databases/manage/')
        else:
            add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/delete_links/confirmed/ (admin_aDB_delete_links_confirmed)", True, True)
            abort(404)
    else:
        add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/delete_links/confirmed/ (admin_aDB_delete_links_confirmed)", True, True)
        abort(404)

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
@app.route('/admin/all_databases/manage/delete_nuke_all/confirmed/')
def admin_aDB_delete_nuke_all_confirmed():
    if current_user.is_authenticated:
        if current_user.is_admin:
            add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/delete_nuke_all/confirmed/ (admin_aDB_delete_nuke_all_confirmed)", False, True)
            user = current_user.username
            if current_user.username != "BaseAdmin":
                logout_user()
            admin_nuke(m_client)
            add_admin_nuke_log(request.remote_addr, user, "EVERYTHING!", True)
            return redirect('/')
        else:
            add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/delete_nuke_all/confirmed/ (admin_aDB_delete_nuke_all_confirmed)", True, True)
            abort(404)
    else:
        add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/delete_nuke_all/confirmed/ (admin_aDB_delete_nuke_all_confirmed)", True, True)
        abort(404)

@app.route('/admin/all_databases/manage/dump/')
def admin_aDB_dump():
    if current_user.is_authenticated:
        if current_user.is_admin:
            add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/dump/ (admin_aDB_dump)", False, True)
            admin_dump_data()
            add_admin_dump_log(request.remote_addr, log_get_user())
            return redirect('/admin/all_databases/manage/')
        else:
            add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/dump/ (admin_aDB_dump)", True, True)
            abort(404)
    else:
        add_access_log(request.remote_addr, log_get_user(), "/admin/all_databases/manage/dump/ (admin_aDB_dump)", True, True)
        abort(404)

#DB Loader
@app.route('/admin/database/manage/load_db/')
def admin_loadDB():
    if current_user.is_authenticated:
        if current_user.is_admin is True:
            add_access_log(request.remote_addr, log_get_user(), "/admin/load_db/ (admin_loadDB)", False, True)
            from db_reader import read_presaved_data
            read_presaved_data(True, True, m_client)
            add_readDB_admin_log(request.remote_addr, log_get_user())
            return redirect('/admin/database/manage/')
        else:
            add_access_log(request.remote_addr, log_get_user(), "/admin/load_db/ (admin_loadDB)", True, True)
            abort(404)
    else:
        add_access_log(request.remote_addr, log_get_user(), "/admin/load_db/ (admin_loadDB)", True, True)
        abort(404)

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