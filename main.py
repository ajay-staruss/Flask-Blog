from flask import Flask,render_template,request,session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail
import json


with open('config.json','r') as c:
    params = json.load(c)["params"]

local_server =True

app = Flask(__name__)
app.config['SECRET_KEY'] = 'redsfsfsfsfis'
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL= True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD = params['gmail-pass']
)
mail = Mail(app)

if(local_server==True):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
db = SQLAlchemy(app)


class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80),nullable=False)
    phone_num = db.Column(db.String(120),  nullable=False)
    email = db.Column(db.String(20), nullable=False)
    mes = db.Column(db.String(120),  nullable=False)
    date = db.Column(db.String(20),  nullable=False)

class Post(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80),nullable=False)
    content = db.Column(db.String(120),  nullable=False)
    date = db.Column(db.String(20), nullable=False)
    file_name = db.Column(db.String(30),  nullable=False)
    slug = db.Column(db.String(20),  nullable=False)

@app.route('/')
def index():
    posts = Post.query.filter_by().all()[0:params['no_of_post']]
    return render_template('index.html',params=params,posts=posts)

@app.route('/about')
def about():
    return render_template('about.html',params=params)

@app.route('/contact', methods=['GET','POST'])
def contact():
    if request.method=='POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        msg = request.form.get('msg')

        entry = Contacts(name=name,email=email,phone_num=phone,mes = msg,date = datetime.now())
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from '+name, sender = email, recipients=[params['gmail-user']], body=msg)
    return render_template('contact.html',params=params)

@app.route('/post/<string:post_slug>', methods = ['GET'])
def post(post_slug):
    p = Post.query.filter_by(slug=post_slug).first()
    return render_template('post.html',params=params, post=p)


@app.route('/dashboard',methods=['GET','POST'])
def dashboard():

    if ('user' in session and session['user'] == params['admin_user']):
        posts = Post.query.all()
        return render_template('dashboard.html',params=params,posts=posts) 

    if request.method=='POST':
        username = request.form.get('uname')
        password = request.form.get('pass')
        if(username== params['admin_user'] and password==params['admin_password']):
            session['user'] = username
            posts = Post.query.all()
            return render_template('dashboard.html',params=params,posts=posts)
    else:
        return render_template('login.html',params=params)


@app.route('/edit/<string:sno>', methods = ['GET','POST'])
def edit(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        if request.method == 'POST':
            box_title = request.form.get('title')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')
            if(sno == '0'):
                post = Post(title = box_title, content = content, file_name = img_file, slug=slug,date = datetime.now)
                db.session.add(post)
                db.session.commit()
        return render_template('edit.html',params=params,sno=sno)
    else:
        return render_template('edit.html',params=params,sno=sno)






app.run(debug=True)

