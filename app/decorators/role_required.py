from functools import wraps
from flask_login import current_user
from flask import abort


def role_required(*roles):
    def wrapper(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            if current_user.user_role not in roles:
                abort(403, "You are not authorized to access this page")
            return func(*args, **kwargs)
        return decorated
    return wrapper