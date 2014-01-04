import os
from flask import render_template, flash, redirect, send_from_directory, g
from app import app
from forms import LoginForm
from app.models.contentMeta import ContentType, Tag

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
@app.route('/list/')
@app.route('/grid/')
@app.route('/filter/')
@app.route('/list/filter/')
@app.route('/grid/filter/')
def main():
    return render_template("main.html", all_tags=Tag.get_all_tags(),
                           content_types=ContentType.get_content_types_with_contents())

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')
