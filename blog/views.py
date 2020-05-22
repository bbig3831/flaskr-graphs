from flask import Flask, render_template, request, flash, redirect, url_for

from blog.models import User

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User(username)

        if not user.register(password):
            flash('A user with that username already exists.')
        else:
            flash('Successfully registered')
            return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login')
def login():
    return 'TODO'


@app.route('/add_post')
def add_post():
    return 'TODO'


@app.route('/like_post/<post_id>')
def like_post(post_id):
    return 'TODO'


@app.route('/profile/<username>')
def profile(username):
    return 'TODO'
