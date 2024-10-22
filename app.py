from flask import Flask, render_template, url_for, request, redirect, abort

#Server Vars
app = Flask(__name__)

#General Routes
#Home/Index
@app.route('/')
def home():
    return render_template('home.html', page_name="Home")

@app.route('/Prices')
def prices():
    return render_template('prices.html', page_name="Prices")

@app.route('/Areas')
def areas():
    return render_template('areas.html', page_name="Areas Covered")

@app.route('/What_You_Need_to_Know')
def wyntk():
    return render_template('wyntk.html', page_name="What You Need to Know")

@app.route('/Contact')
def contact():
    return render_template('contact.html', page_name="What You Need to Know")

#Error Pages
#These pages are only shown when the website encounters an error.
#404 is page not found.
@app.errorhandler(404)
def page_invalid(e):
    return render_template('errors/404.html'), 404

#Launch Website
if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
    #app.run(host="0.0.0.0", debug=True)