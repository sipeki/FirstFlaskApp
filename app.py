from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from os import environ

app = Flask(__name__)

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


@app.route('/')
@app.route('/home')
def home():
    post_data = Posts.query.all()
    return render_template('homepage.html', title="Homepage", posts=post_data)

@app.route('/about')
def about():
    return render_template('about.html', title="About Us")

@app.route('/create')
def create():
    db.create_all()
    post = Posts(f_name='Tadas', l_name='Vaidotas', title='Mr', content='Text line')
    post2 = Posts(f_name='Simon', l_name='Kindlen', title='Mr', content='Another Text line')
    db.session.add(post)
    db.session.add(post2)
    db.session.commit()
    return "Some Lovely data created"

@app.route('/delete')
def delete():
    db.drop_all()
    # db.session.query(Posts).delete()
    db.session.commit()
    return "Eveverything is gone"

if __name__ == '__main__':
    app.run()
