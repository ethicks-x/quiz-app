from app import app
from flask import request, render_template, send_from_directory, redirect, url_for
from flask_login import current_user
# from flask import current_app as app

import os

@app.route('/')
def home():
    if current_user.is_authenticated:
        # Check if user is admin
        if current_user.role == "admin":
            return redirect(url_for("admin.index"))
        else:
            return redirect(url_for("user.dashboard"))
    else:
        return redirect(url_for("auth.login"))


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/images'), 'favicon.ico')