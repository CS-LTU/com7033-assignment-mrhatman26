import ast
from flask import Flask, render_template, url_for, request, redirect, abort
from flask_login import LoginManager, current_user, login_user, logout_user
from user import User
from db_handler import *

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

'''General Routes'''
#Home/Index
@app.route('/')
def home():
    if admin_check_basepass() is False:
        admin_hash_basepass()
    return render_template('home.html', page_name="Home")

'''User Routes'''
#Login
@app.route('/users/login/')
def user_login():
    if current_user.is_authenticated:
        return redirect('/')
    else:
        return render_template('users/login.html', page_name="Login")
@app.route('/users/login/validate/', methods=['POST'])
def user_login_validate():
    if current_user.is_authenticated:
        return redirect('/')
    else:
        userdata = request.get_data()
        userdata = userdata.decode()
        userdata = ast.literal_eval(userdata)
        try:
            if user_check_validate(userdata) is True:
                login_user(User(user_get_id(userdata["username"]), userdata["username"], admin_user_admin_check(userdata["username"])))
                return "success"
            else:
                return "usernotexist"
        except Exception as e:
            print("An error ocurred:\n" + str(e), flush=True)
            return "servererror"

#Signup
@app.route('/users/signup/')
def user_signup():
    if current_user.is_authenticated:
        return redirect('/')
    else:
        return render_template('users/signup.html', page_name="Signup")
@app.route('/users/signup/validate', methods=['POST'])
def user_signup_validate():
    if current_user.is_authenticated:
        return redirect('/')
    else:
        userdata = request.get_data()
        userdata = userdata.decode()
        userdata = ast.literal_eval(userdata)
        try:
            if user_create(userdata) is True:
                return "success"
            else:
                return "userexists"
        except Exception as e:
            print("An error ocurred:\n" + str(e), flush=True)
            return "servererror"
    
#Logout
@app.route('/users/logout/')
def user_logout():
    if current_user.is_authenticated:
        logout_user()
        return redirect('/')
    else:
        return redirect('/')

'''Admin Routes'''
#Main
@app.route('/admin/')
def admin_main():
    if current_user.is_authenticated:
        if current_user.is_admin is True:
            return render_template('/admin/admin_main.html', page_name="Admin Home")
        else:
            abort(404)
    else:
        abort(404)

#DB Loader
@app.route('/admin/load_db/')
def admin_loadDB():
    if current_user.is_authenticated:
        if current_user.is_admin is True:
            from db_reader import read_presaved_data
            read_presaved_data()
            return redirect('/')
        else:
            abort(404)
    else:
        abort(404)

#Error Pages
#These pages are only shown when the website encounters an error.
#404 is page not found.
@app.errorhandler(404)
def page_invalid(e):
    return render_template('errors/404.html'), 404

#Launch Website
if __name__ == '__main__':
    if deployed is True:
        from waitress import serve
        serve(app, host="0.0.0.0", port=5000)
    else:
        app.run(host="0.0.0.0", debug=True)