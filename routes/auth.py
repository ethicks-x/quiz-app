from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_user, logout_user, current_user, login_required
from flask_bcrypt import Bcrypt

from app import app
from models.model import User
from configurations.database import db

from datetime import datetime


auth = Blueprint('auth', __name__, url_prefix='/auth')


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        full_name = request.form["full_name"]
        qualification = request.form["qualification"]
        dob = datetime.strptime(request.form["dob"], "%Y-%m-%d")

        # Hashing Password
        bcrypt = Bcrypt(app)
        pw_hash = bcrypt.generate_password_hash(password).decode()

        # Check if User exists
        user = db.session.query(User).filter(User.username == username).first()
        if user is None:
            # creating user query
            new_user = User(username=username,
                            password=pw_hash,
                            full_name=full_name,
                            qualification=qualification,
                            dob=dob)
            
            # adding the user in database
            db.session.add(new_user)
            db.session.commit()

            # loggin the user in
            login_user(new_user)     

            return redirect(url_for("index"))
            
        else:
            return render_template("auth/register.html", error="username already exists!")

    else:
        # user authentication checked
        if current_user.is_authenticated:
            return redirect(url_for("index"))
        else:
            return render_template("auth/register.html")


@auth.route('/login', methods=['GET', "POST"])
def login():
    if request.method == "POST":
        # fetching form data
        username = request.form("username")
        password = request.form("password")

        # checking for user availiability
        user = User.query.filter(username=username).first()

        if user is None:
            return render_template("auth/login.html", error="username not found!")
        else:
            bcrypt = Bcrypt(app)
            if bcrypt.check_password_hash(user.password, password):
                login_user(user)
                # Redirection to home page
                return redirect(url_for("index"))
            else:
                return render_template("auth/login.html", error="password not matched!")

    else:
        # user authentication checked
        if current_user.is_authenticated:
            return redirect(url_for("index"))
        else:
            return render_template("auth/login.html")


@auth.route('/logout')
def logout():
    # log out user
    logout_user()

    # redirect to login page
    return redirect(url_for("auth.login"))