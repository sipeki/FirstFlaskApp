from flask import Flask
from flask import render_template
app = Flask(__name__)

dummyData = [
    {
        "f_name": "Tadas",
        "l_name": "Vaidotas",
        "title": "Mr",
        "content": "Real nice person ;-)"
    },
{
        "f_name": "Simon",
        "l_name": "Kindlen",
        "title": "Mr",
        "content": "Keep an eye on."
    }
]
@app.route('/')
@app.route('/home')
def home():
    return render_template('homepage.html', title="Homepage", posts=dummyData)

@app.route('/about')
def about():
    return render_template('about.html', title="About Us")


if __name__ == '__main__':
    app.run()
