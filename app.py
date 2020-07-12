from flask import Flask, redirect, url_for, request
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from os import environ
from flask_bcrypt import Bcrypt
from wtforms import ValidationError

from forms import PostsForm, RegistrationForm, UpdateAccountForm, LoginForm
from flask_login import LoginManager, login_user, current_user, logout_user, login_required, UserMixin
from datetime import datetime

app = Flask(__name__)
bcrypt = Bcrypt()
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# make more secure
app.config['SECRET_KEY'] = 'c076a09b61f56e9338a7c7d97244d5b0'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:CODeb9aGb0hrm9eN@35.189.67.84:3306/posts'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://' + \
                                        environ.get('MYSQL_USER') + \
                                        ':' + \
                                        environ.get('MYSQL_PASSWORD') + \
                                        '@' + \
                                        environ.get('MYSQL_HOST') + \
                                        ':' + \
                                        environ.get('MYSQL_PORT') + \
                                        '/' + \
                                        environ.get('MYSQL_DB_NAME')

db = SQLAlchemy(app)
# Then remove the first and last name columns from the Posts table and add these lines to it.
# removed f_name = db.Column(db.String(30), nullable=False)
# l_name = db.Column(db.String(30), nullable=False)

# might need to remove
def validate_email(self, email):
    if email.data != current_user.email:
        user = Users.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already in use')


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.String(300), nullable=False)


    def __repr__(self):
        return ''.join(
            [
                'User ID: ', self.user_id, '\r\n',
                'Title: ', self.title, '\r\n', self.content
            ]
        )


@login_manager.user_loader
def load_user(id):
    return Users.query.get(int(id))


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    f_name = db.Column(db.String(30), nullable=False)
    l_name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(500), nullable=False)
    posts = db.relationship('Posts', backref='author', lazy=True)

    def __repr__(self):
        return ''.join([
            'User ID: ', str(self.id), '\r\n',
            'Email: ', self.email, '\r\n',
            'Name: ', self.first_name, ' ', self.last_name
        ])

# def validate_email(self, email):
#    user = Users.query.filter_by(email=email.data).first()

#    if user:
#        raise ValidationError('Email already in use')

#   modified @app.route('/register', methods=['GET', 'POST'])

@app.route('/register' , methods=['GET', 'POST'])
def register():

    print("reg1")
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()
    print("reg2")
    if form.validate_on_submit():
        hash_pw = bcrypt.generate_password_hash(form.password.data)
        user = Users(
            f_name=form.f_name.data,
            l_name=form.l_name.data,
            email=form.email.data,
            password=hash_pw
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route('/', methods=['GET', 'POST'])
@app.route('/home')
def home():
    post_data = Posts.query.all()
    return render_template('homepage.html', title="Homepage", posts=post_data)

@app.route('/about')
@login_required
def about():
    return render_template('about.html', title="About Us")


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = PostsForm()
    if form.validate_on_submit():
        post_data = Posts(
            title=form.title.data,
            content=form.content.data,
            author=current_user
        )
        db.session.add(post_data)
        db.session.commit()
        return redirect(url_for('home'))
    else:
        return render_template('post.html', title='Add a post', form=form)


@app.route('/createpost')
def createpost():
    db.create_all()
    post = Posts(f_name='Tadas', l_name='Vaidotas', title='Mr', content='Text line')
    post2 = Posts(f_name='Simon', l_name='Kindlen', title='Mr', content='Another Text line')
    db.session.add(post)
    db.session.add(post2)
    db.session.commit()
    return "Some Lovely data created"


@app.route('/create')
def create():
    db.drop_all()
    db.create_all()
    return "Eveverything is gone and tables recreated"


@app.route('/delete')
def delete():
    db.drop_all()
    # db.session.query(Posts).delete()
    db.session.commit()
    return "Everything is gone"


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        print("1 login")
        user = Users.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            print("2 login")
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('home'))
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.f_name = form.f_name.data
        current_user.l_name = form.l_name.data
        current_user.email = form.email.data
        db.session.commit()
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.f_name.data = current_user.f_name
        form.l_name.data = current_user.l_name
        form.email.data = current_user.email
    return render_template('account.html', title='Account', form=form)

@app.route("/account/delete", methods=["GET", "POST"])
@login_required
def account_delete():
    user = current_user.id
    account = Users.query.filter_by(id=user).first()
#   post = Posts.query.filter_by(user_id=user).delete()
    logout_user()
    db.session.delete(account)
#   db.session.delete(post)
    db.session.commit()
    return redirect(url_for('register'))


if __name__ == '__main__':
    app.run()
