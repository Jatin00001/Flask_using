from flask import Flask,render_template,request,session,redirect
from flask_mail import Mail
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
import json
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import math


with open('config.json','r') as c :
    parameter = json.load(c)["parameter"]

app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config['UPLOAD_FOLDER'] = parameter['upload_location']
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
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts)/int(parameter['no_of_post']))
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    posts = posts[(page - 1)*int(parameter['no_of_post']): (page - 1) * int(parameter['no_of_post']) + int(parameter['no_of_post'])]
    if(page == 1):
        prev = "#"
        next = "/?page=" + str(page + 1)
    elif(page == last):
        prev = "/?page=" + str(page - 1)
        next = "#"
    else:
        prev = "/?page=" + str(page - 1)
        next = "/?page=" + str(page + 1)

    return render_template('index.html', parameter = parameter, posts=posts, prev=prev, next=next)

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
        posts = Posts.query.all()
        print("in already post session")
        return render_template('dashboard.html', parameter=parameter, posts=posts)

    if (request.method == 'POST'):
        # print("in post session")
        username = request.form.get('user')
        userpass = request.form.get('password')
        if( (username==parameter['admin-user']) and (userpass == parameter['admin-password'])):
            session['user'] = username
            posts = Posts.query.all()
            return render_template('dashboard.html',parameter=parameter, posts=posts)
    return render_template('login.html', parameter=parameter)
@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', parameter=parameter, post=post)


@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit(sno):
    if "user" in session and session['user'] == parameter['admin-user']:
        # print("in edit session")
        if request.method == "POST":
            # print("form input")
            title = request.form.get('title')
            shead = request.form.get('shead')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')
            date = datetime.now()
            if sno == '0':
                # print("in new post session")
                post = Posts(title=title,subhead=shead, slug=slug, content=content, img_file=img_file, date=date)
                db.session.add(post)
                db.session.commit()
            else:
                print("else edit")
                post = Posts.query.filter_by(sno=sno).first()
                post.title = title
                post.subhead = shead
                post.slug = slug
                post.content = content
                post.img_file = img_file
                post.date = date
                db.session.commit()
                return redirect('/edit/' + sno)

    post = Posts.query.filter_by(sno=sno).first()
    return render_template('edit.html', parameter=parameter,post=post, sno=sno)

@app.route("/uploader", methods=['GET', 'POST'])
def uploader():
    if "user" in session and session['user'] == parameter['admin-user']:
        if request.method == "POST":
            f = request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            return "Uploaded successfully"

@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/dashboard')


@app.route("/delete/<string:sno>" , methods=['GET', 'POST'])
def delete(sno):
    if "user" in session and session['user']==parameter['admin-user']:
        post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect("/dashboard")


if __name__ == '__main__':
    app.run(debug=True,port=615000)