
from flask_login import current_user
from flask import abort
from functools import wraps

def is_admin(f):
    """ Admin permission Required .

    Args:
        f (function): a function to securize. 

    Returns:
        f: Return the wrapped function if accessed by admin user. Otherwise return an abort 403
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):         
        try:       
            if current_user.id == 1 and current_user.username == "admin":
                return f(*args, **kwargs)
            else:
                return abort(403)
        except AttributeError:
            current_user.id = 0            
            return abort(403)
    return decorated_function

def is_user(f):
    """ User permission Required.

    Args:
        f (function): a function to securize. 

    Returns:
        f: Return the wrapped function if accessed by logged-in user but admin. Otherwise return an abort 403
    """
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
    """ Logged-in permission Required.

    Args:
        f (function): a function to securize. 

    Returns:
        f: Return the wrapped function if accessed by logged-in user. Otherwise return an abort 403
    """
    @wraps(f)
    def decorated_function(*args, **kwargs): 
        try:       
            if current_user.is_authenticated:
                return f(*args, **kwargs)
            else:
                return abort(403)
        except AttributeError:
            current_user.id = 0
            return abort(403)
        except IndexError:
         return abort(403)   
    return decorated_function

def get_current_user() -> str:
    """Get the current_user.username if current_user else none

    Returns:
        str: current_user.username or None
    """
    try:
        username = current_user.username        
    except AttributeError:
        username = None
    return username


