"""
Decorators Library
-------------------------
A collection of decorators used by the main
app, created to avoid the unnecessary 
reproduction of code.
"""

from flask import session, flash, redirect, url_for
from functools import wraps


def login_required(f):
    """login_required Ensures that a user is logged in before granting access to user restricted pages

    Will check if a user is logged in and only allow a redirect to the user restricted page if there is 
    a user logged in. If no user is logged in it will chenge the redirect to the home page and flash a 
    login required messege, letting the user know they must login before accessing that endpoint. 
    NOTE: This function should never be called as a function, only used as a decorator above functions 
    who require its functionality to be implemented on entry. Always use a decorator (i.e. @login_required) 
    to invoke this function.

    :param f: The function being decorated. This will be automatically filled when using the @ tag
    :type f: function
    :return: The wrap function, whose contents are the input function, modified to add the functionality of this decorator
    :rtype: function
    """
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('home'))
    return wrap


def logout_required(f):
    """logout_required Ensures that a user is logged out before granting access to non user restricted pages

    Will check if a user is logged out and only allow a redirect to the non user restricted page if there is 
    no user logged in. If a user is logged in it will simply log them out automatically before redirecting to
    the requested endpoint. No logout action on the part of the user is necessary. 
    NOTE: This function should never be called as a function, only used as a decorator above functions 
    who require its functionality to be implemented on entry. Always use a decorator (i.e. @logout_required) 
    to invoke this function.

    :param f: The function being decorated. This will be automatically filled when using the @ tag
    :type f: function
    :return: The wrap function, whose contents are the input function, modified to add the functionality of this decorator
    :rtype: function
    """
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            session.pop('logged_in', None)
            return f(*args, **kwargs)
        else:
            return f(*args, **kwargs)
    return wrap