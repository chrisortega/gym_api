from flask import Flask
from flask_cors import CORS
from routes.api import api_bp
from flask import Flask, render_template
from db import get_db
from dotenv import load_dotenv
import os
load_dotenv(override=True)


app = Flask(__name__)
CORS(app)

db = get_db()

# Register API Blueprint with prefix /api
app.register_blueprint(api_bp, url_prefix="/api")


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/forgot')
def forgot():
    return render_template('forgot.html')

@app.route('/reset')
def reset():    
    return render_template('reset.html')

@app.route("/entries")
def entries():
    return render_template("entries_today.html")

@app.route("/add-entry")
def add_entry_page():
    return render_template("add_entry.html")


@app.route("/manage-users")
def manage_users():
    return render_template("manage_users.html")


@app.route("/user")
def user_page():
    return render_template("user.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
