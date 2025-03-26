from flask import current_app as app
from flask import request, render_template, send_from_directory

@app.route('/')
def home():
    return render_template('index.html')