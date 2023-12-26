from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from urllib.parse import quote_plus
import math
import smtplib

app = Flask(__name__)
password = quote_plus("postgres_password")
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:{password}@localhost:5432/flaskalchemy'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret_key_here'
db = SQLAlchemy(app)

own_email = "your_email"
own_password = "your_password"


class Contacts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    email = db.Column(db.String(35), nullable=False)


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    tagline = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    content = db.Column(db.String(120), nullable=False)
    img_file = db.Column(db.String(12), nullable=True)


class Login(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(), nullable=False)
    password = db.Column(db.String(), nullable=False)


@app.route("/")
def home():
    no_of_posts = 2
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts)/int(no_of_posts))
    page = request.args.get('page')
    if(not str(page).isnumeric()):
        page = 1
    page= int(page)
    posts = posts[(page-1)*int(no_of_posts): (page-1)*int(no_of_posts)+ int(no_of_posts)]
    #Pagination Logic
    if (page==1):
        prev = "#"
        next = "/?page="+ str(page+1)
    elif(page==last):
        prev = "/?page=" + str(page - 1)
        next = "#"
    else:
        prev = "/?page=" + str(page - 1)
        next = "/?page=" + str(page + 1)
    return render_template('index.html', posts=posts, prev=prev, next=next)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('pass')
        # Check if the user exists in the database
        user = Login.query.filter_by(email=email).first()
        if user:
            # Check if the provided password matches the user's password
            if user.password == password:
                # Set the 'user' session variable and render the index page
                session['user'] = email
                posts = Posts.query.all()
                return render_template("dashboard.html", posts=posts)
            else:
                # Password doesn't match, render the login page
                return render_template('login.html')
        else:
            # User doesn't exist, create a new user and render the index page
            new_user = Login(email=email, password=password)
            db.session.add(new_user)
            db.session.commit()

            session['user'] = email
            posts = Posts.query.all()
            return render_template("dashboard.html", posts=posts)
    else:
        return render_template("login.html")


@app.route('/dashboard')
def dashboard():
    posts = Posts.query.all()
    return render_template("dashboard.html", posts=posts)


@app.route('/edit/<string:sno>', methods=['GET', 'POST'])
def edit(sno):
    if request.method == "POST":
        box_title = request.form.get('title')
        tline = request.form.get('tagline')
        slug = request.form.get('slug')
        content = request.form.get('content')
        date = datetime.now()
        img_file = request.form.get('img_file')

        if(sno == '0'):
            posts = Posts(title=box_title, slug=slug, tagline=tline, date=date, content=content, img_file=img_file)
            db.session.add(posts)
            db.session.commit()
        else:
            post = Posts.query.filter_by(id=sno).first()
            post.title = box_title
            post.tagline = tline
            post.slug = slug
            post.content = content
            post.date = date
            post.img_file = img_file
            db.session.commit()
            return redirect('/edit/' + sno)
    post = Posts.query.filter_by(id=sno).first()
    return render_template('edit.html', post=post, sno=sno)


@app.route('/post/<string:post_slug>', methods=['GET'])
def post(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template("post.html", post=post)


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if(request.method == 'POST'):
        '''Add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        # send_email(name, email, phone, message)
        entry = Contacts(name=name, phone_num=phone, msg=message, date=datetime.now(),email=email)
        db.session.add(entry)
        db.session.commit()
    return render_template('contact.html')

 def send_email(name, email, phone, msg):
     send_msg = f"Subject:new message\n\nName: {name}\nPhone: {phone}\nMessage:{msg}"
     with smtplib.SMTP("smtp.gmail.com", 587) as connection:
         connection.starttls()
         connection.login(own_email, own_password)
         connection.sendmail(own_email, email, send_msg)


@app.route('/delete/<string:id>', methods=['GET', 'POST'])
def delete(id):
    if 'user' in session:
        post = Posts.query.filter_by(id=id).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')


@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/login')



@app.route('/about')
def about():
    return render_template("about.html")


if __name__ == '__main__':
    app.run(debug=True)
