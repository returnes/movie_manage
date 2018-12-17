from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
# app.debug = True
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:000000@127.0.0.1:3306/movie"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_POOL_SIZE']=100
app.config['SQLALCHEMY_MAX_OVERFLOW']=20
app.config['DEBUG']=True
app.config['SECRET_KEY'] = "asdfghjkl"
app.config["UP_DIR"] = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/uploads/")
app.config["UP_DIR_USER"] = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/uploads/users/")

db = SQLAlchemy(app)
CSRFProtect(app)
from app.admin import admin as admin_blueprint
from app.home import home as home_blueprint

app.register_blueprint(admin_blueprint, url_prefix="/admin")
app.register_blueprint(home_blueprint)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('home/404.html'), 404
