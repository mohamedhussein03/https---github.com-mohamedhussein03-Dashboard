from flask_login import current_user
from flask import abort

def admin_required():
    if current_user.role != "admin":
        abort(403)
