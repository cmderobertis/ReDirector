from flask import Flask, render_template, make_response, session, request, redirect, url_for, flash
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
import re
import requests
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = f"{os.getenv('SECRET_KEY')}"
bcrypt = Bcrypt(app)
in_development = True


if in_development:
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:{os.getenv("MYSQL_PW")}@localhost:3306/redirector'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = ''

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Error handling


@app.errorhandler(404)
def not_found(err):
    return make_response(render_template("404.html"), 404)


# Constants
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

# .env config
load_dotenv()

# Global Functions


def verify_logged_in():
    if not 'user_id' in session:
        return redirect('/login')
