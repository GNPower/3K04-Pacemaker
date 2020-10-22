from flask import session, flash, redirect, url_for
from functools import wraps

#login required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('home'))
    return wrap

#login required decorator
def logout_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            session.pop('logged_in', None)
            return f(*args, **kwargs)
        else:
            return f(*args, **kwargs)
    return wrap