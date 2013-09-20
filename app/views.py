from flask import render_template, flash, redirect, Request
from app import app
from forms import LoginForm
from util.get_data import requestRssData, loadDatabase, cleanSoupHtml
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
    contents = Content.query.all()
    return render_template("main.html", contents = contents)
