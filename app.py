from flask import Flask, redirect, url_for, request
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from os import environ
from flask_bcrypt import Bcrypt
from forms import PostsForm, RegistrationForm, LoginForm
from flask_login import LoginManager, login_user, current_user, logout_user, login_required, UserMixin

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


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    f_name = db.Column(db.String(30), nullable=False)
    l_name = db.Column(db.String(30), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(300), nullable=False, unique=True)

    def __repr__(self):
        return ''.join(
            [
                'Title:  ' + self.title + '\n'
                'Name:  ' + self.f_name + ' ' + self.l_name + '\n'
                'Content: ' + self.content
            ]
        )


@login_manager.user_loader
def load_user(id):
    return Users.query.get(int(id))


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(500), nullable=False, unique=True)
    password = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return ''.join(['UserID: ', str(self.id), '\r\n', 'Email: ',self.email])

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hash_pw = bcrypt.generate_password_hash(form.password.data)

        user = Users(email=form.email.data, password=hash_pw)

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route('/')
@app.route('/home')
def home():
    post_data = Posts.query.all()
    return render_template('homepage.html', title="Homepage", posts=post_data)

@app.route('/about')
def about():
    return render_template('about.html', title="About Us")


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = PostsForm()
    if form.validate_on_submit():
        post_data = Posts(
            f_name=form.f_name.data,
            l_name=form.l_name.data,
            title=form.title.data,
            content=form.content.data,
        )
        db.session.add(post_data)
        db.session.commit()
        return redirect(url_for('home'))
    else:
        return render_template('post.html', title='Add a post', form=form)


@app.route('/create')
def create():
    db.create_all()
    post = Posts(f_name='Tadas', l_name='Vaidotas', title='Mr', content='Text line')
    post2 = Posts(f_name='Simon', l_name='Kindlen', title='Mr', content='Another Text line')
    db.session.add(post)
    db.session.add(post2)
    db.session.commit()
    return "Some Lovely data created"

@app.route('/create2')
def create2():
    db.drop_all()
    db.create_all()
    return "Eveverything is gone"

@app.route('/delete')
def delete():
    db.drop_all()
    # db.session.query(Posts).delete()
    db.session.commit()
    return "Eveverything is gone"

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

if __name__ == '__main__':
    app.run()
