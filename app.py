from flask import Flask, render_template
from flask_cors import CORS
from routes import all_blueprints
from db import get_db
from dotenv import load_dotenv
import os
load_dotenv(override=True)


app = Flask(__name__)


db = get_db()

# Register all API Blueprints with prefix /api
for bp in all_blueprints:
    app.register_blueprint(bp, url_prefix="/api")


CORS(
    app,
    resources={r"/api/*": {
        "origins": "*",   # or "http://localhost:8100" for Ionic
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": "*"
    }}
)

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

@app.route("/edit-gym")
def edit_gym_page():
    return render_template("edit_gym.html")

@app.route("/add-user")
def add_user():
    return render_template("add_user.html")

@app.route("/biometrics")
def biometrics():
    return render_template("user_biometrics.html")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 3001))
    app.run(host="0.0.0.0", port=port, debug=True)
