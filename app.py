import ast
from flask import Flask, render_template, url_for, request, redirect, abort
from flask_login import LoginManager, current_user, login_user, logout_user
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
        return User(user_check[0], user_check[1])
########################################Todo: Finish login and signup.

'''General Routes'''
#Home/Index
@app.route('/')
def home():
    return render_template('home.html', page_name="Home")

'''User Routes'''
#Signup
@app.route('/users/signup/')
def user_signup():
    if current_user.is_authenticated:
        return redirect('/')
    else:
        return render_template('users/signup.html', page_name="Signup")
@app.route('/users/signup/validate', methods=['POST'])
def user_signup_validate():
    userdata = request.get_data()
    userdata = userdata.decode()
    userdata = ast.literal_eval(userdata)
    try:
        print(userdata)
        return "success"
    except:
        return "servererror"

'''Admin Routes'''
#Main
@app.route('/admin/')
def admin_main():
    if current_user.is_authenticated:
        return render_template('/admin/admin_main.html', page_name="Admin Home")
    else:
        abort(404)

#DB Loader
@app.route('/admin/load_db/')
def admin_loadDB():
    if current_user.is_authenticated:
        from db_reader import read_presaved_data
        read_presaved_data()
        return redirect('/')
    else:
        #abort(404)
        from db_reader import read_presaved_data
        read_presaved_data()
        return redirect('/')

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