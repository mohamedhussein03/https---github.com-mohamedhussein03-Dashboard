from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, UserMixin
from app.extensions import login_manager

auth_bp = Blueprint("auth", __name__)

class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

USERS = {
    "1": User("1", "admin", "admin"),
    "2": User("2", "guest", "viewer")
}

@login_manager.user_loader
def load_user(user_id):
    return USERS.get(user_id)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        action = request.form.get("action")

        if action == "guest":
            user = USERS["2"]
            login_user(user)
            return redirect(url_for("main.dashboard"))

        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "00123456":
            user = USERS["1"]
            login_user(user)
            return redirect(url_for("main.dashboard"))

        flash("Invalid credentials")

    return render_template("auth/login.html")

@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))  
