from flask import Flask
from flask import render_template
app = Flask(__name__)


@app.route('/')
@app.route('/home')
def hello_world():
    return render_template('homepage.html', title="Homepage")


if __name__ == '__main__':
    app.run()
