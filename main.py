from flask import Flask,render_template,request
import json
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime



with open('config.json','r') as c :
    parameter = json.load(c)["parameter"]

app = Flask(__name__)
if(parameter['local_server']):
    app.config['SQLALCHEMY_DATABASE_URI'] = parameter['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = parameter['production_uri']
db = SQLAlchemy(app)

class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    email = db.Column(db.String(20), nullable=False)

@app.route("/")
def home():
    return render_template('index.html', parameter = parameter)

@app.route("/contact",  methods = ['GET', 'POST'])
def contact():
    if (request.method == 'POST'):
        '''Add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone_no')
        message = request.form.get('message')
        entry = Contacts(name=name, phone_num=phone, msg=message, date=datetime.now(), email=email)
        db.session.add(entry)
        db.session.commit()
    return render_template('contact.html', parameter = parameter)

@app.route("/about")
def about():
    return render_template('about.html', parameter = parameter)

@app.route("/post")
def post():
    return render_template('post.html', parameter = parameter)

if __name__ == '__main__':
    app.run(debug=True,port=615000)