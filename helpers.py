from functools import wraps
from flask import redirect, render_template, request, session

import re

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function

def is_valid_userName(username):
    username_regex = re.compile(r"^[a-zA-Z0-9]{4,}$")
    return bool(username_regex.match(username))

def is_valid_email(email):
    email_regex = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    return bool(email_regex.match(email))