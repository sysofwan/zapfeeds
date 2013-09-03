from flask import render_template
from app import app

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