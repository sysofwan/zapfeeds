import os
from flask import render_template, flash, redirect, send_from_directory
from app import app
from forms import LoginForm
from app.models.Content import Content

@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for OpenID="' + form.openid.data + '", remember_me=' + str(form.remember_me.data))
        return redirect('/index')
    return render_template('login.html', 
        title = 'Sign In',
        form = form)

@app.route('/')
def main():
    contents = Content.getFrontPage()
    print "oi!"
    return render_template("main.html", contents = contents)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')
