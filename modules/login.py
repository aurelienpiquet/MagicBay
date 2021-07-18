
from flask_login import current_user
from flask import abort
from functools import wraps

""" Wrapper pour current_user """

def is_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):         
        try:       
            if current_user.id == 1:
                return f(*args, **kwargs)
            else:
                return abort(403)
        except AttributeError:
            current_user.id = 0            
            return abort(403)
    return decorated_function

def is_user(f):
    @wraps(f)
    def decorated_function(*args, **kwargs): 
        try:       
            if current_user.id > 1:
                return f(*args, **kwargs)
            else:
                return abort(403)
        except AttributeError:
            current_user.id = 0
            return abort(403)
    return decorated_function

def is_logged(f):
    @wraps(f)
    def decorated_function(*args, **kwargs): 
        try:       
            if current_user:
                return f(*args, **kwargs)
            else:
                return abort(403)
        except AttributeError:
            current_user.id = 0
            return abort(403)
        except IndexError:
         return abort(403)   
    return decorated_function

def get_current_user():
    try:
        username = current_user.username        
    except AttributeError:
        username = None
    return username


