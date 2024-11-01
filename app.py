import ast
from flask import Flask, render_template, url_for, request, redirect, abort
from flask_login import LoginManager, current_user, login_user, logout_user
from user import User
from db_handler import *
from access_logger import *
from mongodb import *
from misc import clean_subdata

'''Server Vars'''
app = Flask(__name__)
app.secret_key = "HealthyIGuess"
deployed = False

'''Login Manager'''
login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_fuser(id):
    user_check = user_check_reconfirm(id)
    if len(user_check) <= 0:
        return None
    else:
        return User(user_check[0], user_check[1], bool(user_check[2]))
    
def log_get_user():
    if hasattr(current_user, 'username'):
        return current_user.username
    else:
        return "Annonymous"

'''General Routes'''
#Home/Index
@app.route('/')
def home():
    if admin_check_basepass() is False:
        admin_hash_basepass()
    add_access_log(request.remote_addr, log_get_user(), "/ (home)", False, False)
    return render_template('home.html', page_name="Home")

#Data Submission
@app.route('/submission/')
def submission():
    if current_user.is_authenticated:
        add_access_log(request.remote_addr, current_user.username, "/submission/ (submission)", False, False)
        return render_template('submission.html', page_name="Submission", already_submitted=link_check_exists(current_user.id, False))
    else:
        add_access_log(request.remote_addr, current_user.username, "/submission/ (submission)", True, False)
        return redirect('/users/login/')
@app.route('/submission/validate/', methods=['POST'])
def submission_validate():
    if current_user.is_authenticated:
        subdata = request.get_data()
        subdata = subdata.decode()
        subdata = ast.literal_eval(subdata)
        add_access_log(request.remote_addr, current_user.username, "/submission/validate/ (submission_validate)", False, False)
        mysql_done = False
        try:
            clean_subdata(subdata)
            print(subdata, flush=True)
            mysql_id = insert_new_patient(subdata, current_user.id)
            subdata["MySQL_ID"] = mysql_id
            mysql_done = True
            add_new_patient_log(request.remote_addr, current_user.username, False, False)
            mongo_insert(subdata)
            add_new_patient_log(request.remote_addr, current_user.username, False, True)
            return "success"
        except Exception as e:
            add_new_patient_log(request.remote_addr, current_user.username, True, mysql_done)
            add_error_log(request.remote_addr, current_user.username, "Submission data insertion failed.", e)
            return "servererror"
    else:
        add_access_log(request.remote_addr, current_user.username, "/submission/validate/ (submission_validate)", True, False)
        return redirect('/users/login/')
    
@app.route('/data/view/')
def view_data():
    if current_user.is_authenticated:
        add_access_log(request.remote_addr, current_user.username, "/data/view/ (view_data)", False, False)
        return render_template('data.html', page_name="Submitted Data", patient_data=mongo_find_all(False))
    else:
        add_access_log(request.remote_addr, current_user.username, "/data/view/ (view_data)", True, False)
        return redirect('/users/login/')
    
'''User Routes'''
#Login
@app.route('/users/login/')
def user_login():
    if current_user.is_authenticated:
        add_access_log(request.remote_addr, current_user.username, "/users/login/ (user_login)", True, False)
        return redirect('/')
    else:
        add_access_log(request.remote_addr, log_get_user(), "/users/login/ (user_login)", False, False)
        return render_template('users/login.html', page_name="Login")
@app.route('/users/login/validate/', methods=['POST'])
def user_login_validate():
    if current_user.is_authenticated:
        add_access_log(request.remote_addr, current_user.username, "/users/login/validate/ (user_login_validate)", True, False)
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
        add_access_log(request.remote_addr, current_user.username, "/users/signup/ (user_signup)", True, False)
        return redirect('/')
    else:
        add_access_log(request.remote_addr, log_get_user(), "/users/signup/ (user_signup)", False, False)
        return render_template('users/signup.html', page_name="Signup")
@app.route('/users/signup/validate/', methods=['POST'])
def user_signup_validate():
    if current_user.is_authenticated:
        add_access_log(request.remote_addr, current_user.username, "/users/signup/validate/ (user_signup_validate)", True, False)
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
        add_access_log(request.remote_addr, current_user.username, "/users/account/ (user_account)", False, False)
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
        add_access_log(request.remote_addr, current_user.username, "/users/account/modify/ (user_modify)", False, False)
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
        add_access_log(request.remote_addr, current_user.username, "/users/account/modify/validate/ (user_modify_validate)", False, False)
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
    
@app.route('/users/account/submission_delete/')
def delete_submissionconfirm():
    if current_user.is_authenticated:
        add_access_log(request.remote_addr, current_user.username, "/users/account/submission_delete/ (delete_submissionconfirm)", False, False)
        return render_template('delete_submission.html', page_name="Delete Submission Confirmation")
    else:
        add_access_log(request.remote_addr, current_user.username, "/users/accout/submission_delete/ (delete_submissionconfirm)", True, False)
        abort(404)
@app.route('/users/account/submission_delete/confirmed/')
def delete_submission_confirmed():
    if current_user.is_authenticated:
        if link_check_exists(current_user.id, False):
            add_access_log(request.remote_addr, current_user.username, "/users/account/submission_delete/confirmed/ (delete_submission_confirmed)", False, False)
            patient_id = link_get(current_user.id)["patient_id"]
            admin_delete_patient_data(patient_id)
            add_delete_db_log(request.remote_addr, current_user.username, False, patient_id, False)
            mongo_delete({"MySQL_ID": int(patient_id)})
            add_delete_db_log(request.remote_addr, current_user.username, False, patient_id, False)
            return redirect('/users/account/')
        else:
            add_access_log(request.remote_addr, current_user.username, "/users/account/submission_delete/confirmed/ (delete_submission_confirmed)", True, False)
            return redirect('/users/account/')
    else:
        add_access_log(request.remote_addr, current_user.username, "/users/account/submission_delete/confirmed/ (delete_submission_confirmed)", True, False)
        abort(404)
    
#Delete
@app.route('/users/account/delete/')
def user_deleteconfirm():
    if current_user.is_authenticated:
        add_access_log(request.remote_addr, current_user.username, "/users/account/delete/ (user_deleteconfirm)", False, False)
        return render_template('/users/delete.html', page_name="Delete Confirmation")
    else:
        add_access_log(request.remote_addr, log_get_user(), "/users/account/delete/ (user_deleteconfirm)", True, False)
        abort(404)
@app.route('/users/account/delete/confirmed/')
def user_delete():
    if current_user.is_authenticated:
        add_access_log(request.remote_addr, current_user.username, "/users/account/delete/confirmed/ (user_delete)", False, False)
        temp_user_id = current_user.id
        add_login_log(request.remote_addr, current_user.username, False, True)
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
        add_access_log(request.remote_addr, current_user.username, "/users/logout/ (user_logout)", False, False)
        add_login_log(request.remote_addr, current_user.username, False, True)
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
            add_access_log(request.remote_addr, current_user.username, "/admin/ (admin_main)", False, True)
            return render_template('/admin/admin_main.html', page_name="Admin: Home")
        else:
            add_access_log(request.remote_addr, current_user.username, "/admin/ (admin_main)", True, True)
            abort(404)
    else:
        add_access_log(request.remote_addr, log_get_user(), "/admin/ (admin_main)", True, True)
        abort(404)
    
#User Management
@app.route('/admin/users/')
def admin_user_management():
    if current_user.is_authenticated:
        if current_user.is_admin is True:
            add_access_log(request.remote_addr, current_user.username, "/admin/users/ (admin_user_management)", False, True)
            return render_template('/admin/admin_user_management.html', page_name="Admin: User Management", userdata=user_get_all())
        else:
            add_access_log(request.remote_addr, current_user.username, "/admin/users/ (admin_user_management)", True, True)
            abort(404)
    else:
        add_access_log(request.remote_addr, log_get_user(), "/admin/users/ (admin_user_management)", True, True)
        abort(404)
#Change Admin Status
@app.route('/admin/users/makeadmin/user_id=<user_id>')
def admin_user_apply_admin(user_id):
    if current_user.is_authenticated:
        if current_user.is_admin is True:
            add_access_log(request.remote_addr, current_user.username, "/admin/users/makeadmin/user_id=" + str(user_id) + " (admin_user_apply_admin)", False, True)
            if admin_apply_admin_user(user_id) is True:
                add_user_admin_log(request.remote_addr, user_get_username(user_id), False, False)
            else:
                add_user_admin_log(request.remote_addr, user_get_username(user_id), False, True)
            return redirect('/admin/users/')
        else:
            add_access_log(request.remote_addr, current_user.username, "/admin/users/makeadmin/user_id=" + str(user_id) + " (admin_user_apply_admin)", True, True)
            abort(404)
    else:
        add_access_log(request.remote_addr, log_get_user(), "/admin/users/makeadmin/user_id=" + str(user_id) + " (admin_user_apply_admin)", True, True)
        abort(404)
#Delete
@app.route('/admin/users/delete/user_id=<user_id>')
def admin_user_delete(user_id):
    if current_user.is_authenticated:
        if current_user.is_admin is True:
            add_access_log(request.remote_addr, current_user.username, "/admin/users/delete/user_id=" + str(user_id) + " (admin_user_delete)", False, True)
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
            add_access_log(request.remote_addr, current_user.username, "/admin/users/delete/user_id=" + str(user_id) + " (admin_user_delete)", True, True)
            abort(404)
    else:
        add_access_log(request.remote_addr, log_get_user(), "/admin/users/delete/user_id=" + str(user_id) + " (admin_user_delete)", True, True)
        abort(404)

#Patient Data Management
@app.route('/admin/database/manage/')
def admin_database_management():
    if current_user.is_authenticated:
        if current_user.is_admin:
            add_access_log(request.remote_addr, current_user.username, "/admin/database/manage/ (admin_database_management)", False, True)
            patient_data = admin_get_patient_data()
            links = link_get_all()
            if links is not None and len(links) >= 1:
                for link in links:
                    for patient in patient_data:
                        if patient["id"] == link["patient_id"]:
                            patient["user_link"] = link["user_name"]
            return render_template('/admin/admin_patient_management.html', page_name="Admin: Patient Data Management (MySQL)", patient_data=patient_data, is_mongodb=False)
        else:
            add_access_log(request.remote_addr, current_user.username, "/admin/database/manage/ (admin_database_management)", True, True)
            abort(404)
    else:
        add_access_log(request.remote_addr, log_get_user(), "/admin/database/manage/ (admin_database_management)", True, True)
        abort(404)
@app.route('/admin/database/manage/mongodb/')
def admin_database_management_mongodb():
    if current_user.is_authenticated:
        if current_user.is_admin:
            add_access_log(request.remote_addr, current_user.username, "/admin/database/manage/mongodb/ (admin_database_management_mongodb)", False, True)
            return render_template('/admin/admin_patient_management.html', page_name="Admin: Patient Data Management (MongoDB)", patient_data=mongo_find_all(True), is_mongodb=True)
        else:
            add_access_log(request.remote_addr, current_user.username, "/admin/database/manage/ (admin_database_management)", True, True)
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
            add_delete_db_log(request.remote_addr, current_user.username, False, patient_id, True)
            mongo_delete({"MySQL_ID": int(patient_id)})
            add_delete_db_log(request.remote_addr, current_user.username, True, patient_id, True)
            return redirect('/admin/database/manage/')
        else:
            add_access_log(request.remote_addr, log_get_user(), "/admin/database/delete/patient_id=" + str(patient_id) + " (admin_database_delete)", True, True)
            abort(404)
    else:
        add_access_log(request.remote_addr, log_get_user(), "/admin/database/delete/patient_id=" + str(patient_id) + " (admin_database_delete)", True, True)
        abort(404)
        

#DB Loader
@app.route('/admin/database/manage/load_db/')
def admin_loadDB():
    if current_user.is_authenticated:
        if current_user.is_admin is True:
            add_access_log(request.remote_addr, current_user.username, "/admin/load_db/ (admin_loadDB)", False, True)
            from db_reader import read_presaved_data
            read_presaved_data()
            add_readDB_admin_log(request.remote_addr, current_user.username)
            return redirect('/admin/database/manage/')
        else:
            add_access_log(request.remote_addr, current_user.username, "/admin/load_db/ (admin_loadDB)", True, True)
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