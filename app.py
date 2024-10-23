from flask import Flask, render_template, url_for, request, redirect, abort

#Server Vars
app = Flask(__name__)

'''General Routes'''
#Home/Index
@app.route('/')
def home():
    return render_template('home.html', page_name="Home")

'''Admin Routes'''
@app.route('/admin/')
def admin_main():
    return render_template('/admin/admin_main.html', page_name="Admin Home")

#Error Pages
#These pages are only shown when the website encounters an error.
#404 is page not found.
@app.errorhandler(404)
def page_invalid(e):
    return render_template('errors/404.html'), 404

#Launch Website
if __name__ == '__main__':
    #from waitress import serve
    #serve(app, host="0.0.0.0", port=5000)
    app.run(host="0.0.0.0", debug=True)