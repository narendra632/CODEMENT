from flask import Flask, render_template, session, request, redirect, flash
import json
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import json


app = Flask(__name__)

#JSON file
with open("config.json", "r") as c:
    params= json.load(c)["params"]

local_server=True

#Key for Admin login
app.secret_key = "super-secret-key"


#Local Host
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params["local_uri"]
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params["prod_uri"]
    

db = SQLAlchemy(app)


#Contact Database
class Contacts(db.Model):
    sr_no = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    message = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)


#Home
@app.route("/", methods = ['GET', 'POST'])
def home():
    if(request.method=='POST'):
        '''adding entry to database'''
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        add = timedelta(hours=5, minutes=30)
        entry = Contacts(name=name, email=email, date=datetime.now() + add,  message=message)
        db.session.add(entry)
        db.session.commit()
        flash("Your message was sent successfully. Thanks!", "success")
    return render_template("index.html")


#Admin Login page
@app.route("/login", methods = ['GET','POST'])
def contact():
    return render_template("login.html")


#View Contacts
@app.route("/dashboard", methods = ['GET','POST'])
def dashboard():
    if ('user' in session and session['user'] == params['admin_name']):
        contacts = Contacts.query.all()
        return render_template("adminpanel.html", params=params, contacts=contacts)

    if request.method=='POST':
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        if (username == params['admin_name'] and userpass == params['admin_password']):
            session['user'] = username 
            contacts = Contacts.query.all()
            return render_template("adminpanel.html", params=params, contacts=contacts)
    return render_template("login.html", params=params)


#Contact message Deleter
@app.route("/condel/<string:sr_no>", methods = ['GET', 'POST'])
def condel(sr_no):
    if ('user' in session and session['user'] == params['admin_name']):
        contact = Contacts.query.filter_by( sr_no = sr_no).first()
        db.session.delete(contact)
        db.session.commit()
        return redirect('/dashboard')


#LOGOUT Button
@app.route("/logout")
def logout():
    session.pop('user')
    return redirect("/")

app.run(debug=True)