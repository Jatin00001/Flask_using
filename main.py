from flask import Flask,render_template,request,session
from flask_mail import Mail
import json
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime



with open('config.json','r') as c :
    parameter = json.load(c)["parameter"]

app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = parameter['gmail-user'],
    MAIL_PASSWORD = parameter['gmail-password']
)
mail = Mail(app)
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

class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    subhead = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img_file = db.Column(db.String(12), nullable=True)
@app.route("/")
def home_route():
    posts = Posts.query.filter_by().all()[0:parameter['no_of_post']]
    return render_template('index.html', parameter = parameter, posts=posts)

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
        '''
            mail.send_message('New message from ' + name,
                          sender=email,
                          recipients=[parameter['gmail-user']],
                          body = message + "\n" + phone
                          )
        mail.send(msg)
        '''
    return render_template('contact.html', parameter = parameter)

@app.route("/about")
def about():
    return render_template('about.html', parameter = parameter)
# @app.route("/login")
# def login_route():
#     return render_template('login.html', parameter = parameter)

@app.route("/dashboard", methods = ['GET', 'POST'])
def dashboard():
    if "user" in session and session['user'] == parameter['admin-user']:
        return render_template('dashboard.html', parameter=parameter)

    if (request.method == 'POST'):
        print("in post session")
        username = request.form.get('user')
        userpass = request.form.get('password')
        if( (username==parameter['admin-user']) and (userpass == parameter['admin-password'])):
            session['user'] = username
            return render_template('dashboard.html',parameter=parameter, )
    return render_template('login.html', parameter=parameter)
@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', parameter=parameter, post=post)

if __name__ == '__main__':
    app.run(debug=True,port=615000)