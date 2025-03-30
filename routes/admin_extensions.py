from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from routes.admin import admin_bp, login_admin_required
from models.model import Subject, Chapter, Quiz

@admin_bp.route('/')
@admin_bp.route('')
@login_admin_required
def index():
    return render_template("admin/index.html", user=current_user)
