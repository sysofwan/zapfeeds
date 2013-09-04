from flask import render_template, flash, redirect, Request
from app import app
from forms import LoginForm

@app.route('/')
@app.route('/index')
def index():
    user = { 'nickname': 'medaddy' } # fake user
    contents = [ # fake array of posts
        { 
            'title': 'Portalnd time!', 
            'body': 'Beautiful day in Portland!' 
        },
        { 
            'title': 'Movie reviews', 
            'body': 'The Avengers movie was so cool!' 
        }
    ]
    return render_template("index.html",
        title = 'Home',
        user = user,
        contents = contents)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for OpenID="' + form.openid.data + '", remember_me=' + str(form.remember_me.data))
        return redirect('/index')
    return render_template('login.html', 
        title = 'Sign In',
        form = form)
