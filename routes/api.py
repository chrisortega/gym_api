import random
import string
from flask import Blueprint, request, jsonify
from db import get_db
from utils.auth import authenticate_token, generate_access_token
import bcrypt
import base64
from datetime import datetime
import base64
from flask import request, jsonify
from utils.auth import authenticate_token
from db import get_db


api_bp = Blueprint("api", __name__)
@api_bp.route("/", methods=["GET"])
def index():
    return jsonify({"name":"api"})

# ---------------- USERS ----------------
@api_bp.route("/users", methods=["POST"])
def add_user():
    data = request.json
    name, exp, gym_id = data.get("name"), data.get("exp"), data.get("gym_id")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, exp, gym_id) VALUES (%s, %s, %s)", (name, exp, gym_id))
    conn.commit()
    return jsonify({"message": "User inserted successfully.", "id": cursor.lastrowid}), 200


@api_bp.route("/users", methods=["PUT"])
@authenticate_token
def update_user2():
    data = request.json
    user_id, name, exp = data.get("id"), data.get("name"), data.get("exp")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET name=%s, exp=%s WHERE id=%s", (name, exp, user_id))
    conn.commit()
    return jsonify({"message": "User updated successfully."}), 200


@api_bp.route("/users/<int:user_id>", methods=["GET"])
@authenticate_token
def get_user(user_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT users.exp, users.id,users.name, gym.name AS gym_name
        FROM users JOIN gym ON users.gym_id = gym.id
        WHERE users.id = %s
    """, (user_id,))    
    user = cursor.fetchone()
    
    return jsonify(user or {}), 200


@api_bp.route("/entries/today/<int:gym_id>", methods=["GET"])
@authenticate_token
def get_today_entries(gym_id):
    from db import get_db

    # Extract pagination params with defaults
    limit = int(request.args.get("limit", 10))
    offset = int(request.args.get("offset", 0))

    query = """
        SELECT entries.*, users.name, users.exp,  users.id AS user_id
        FROM entries
        JOIN users ON entries.users_id = users.id
        JOIN gym ON entries.gym_id = gym.id
        WHERE DATE(day) = CURDATE() AND gym.id = %s
        LIMIT %s OFFSET %s
    """

    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, (gym_id, limit, offset))
        results = cursor.fetchall()
        print(results)
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@api_bp.route("/entries", methods=["POST"])
@authenticate_token
def add_entry():
    from db import get_db

    data = request.json
    user_id = data.get("user_id")
    gym_id = data.get("gym_id")

    if not user_id or not gym_id:
        return jsonify({"error": "Missing user_id or gym_id"}), 400

    # Check if user belongs to this gym
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id FROM users WHERE id = %s AND gym_id = %s", (user_id, gym_id))
        user = cursor.fetchone()
        if not user:
            return jsonify({"error": "Este usuario no está en este gimnasio"}), 426

        # Insert entry
        cursor.execute("INSERT INTO entries (users_id, gym_id) VALUES (%s, %s)", (user_id, gym_id))
        conn.commit()

        return jsonify({
            "message": "Entry registered successfully",
            "id": cursor.lastrowid,
            "user_id": user_id,
            "entry_date": str(datetime.now().date())
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@api_bp.route("/entries/user/<int:user_id>", methods=["GET"])
@authenticate_token
def get_entries_by_user(user_id):
    from db import get_db
    query = """
        SELECT entries.*, gym.name AS gym_name
        FROM entries
        JOIN gym ON entries.gym_id = gym.id
        WHERE entries.users_id = %s
        ORDER BY day DESC
    """
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, (user_id,))
        results = cursor.fetchall()
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# ---------------- GYMS ----------------
@api_bp.route("/gyms", methods=["GET"])
@authenticate_token
def get_gyms():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM gym")
    return jsonify(cursor.fetchall()), 200


@api_bp.route("/gym/<int:gym_id>", methods=["GET"])
@authenticate_token
def get_gym(gym_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM gym WHERE id = %s", (gym_id,))
    gym = cursor.fetchone()
    return jsonify(gym or {}), 200

@api_bp.route("/users/gym/<int:gym_id>", methods=["GET"])
@authenticate_token
def get_users_by_gym(gym_id):
    from db import get_db

    query = """
        SELECT users.id, users.name, users.exp, gym.id AS gym_id
        FROM users
        JOIN gym ON users.gym_id = gym.id
        WHERE gym_id = %s
    """

    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, (gym_id,))
        users = cursor.fetchall()
        return jsonify(users), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@api_bp.route("/users/<int:user_id>", methods=["DELETE"])
@authenticate_token
def delete_user(user_id):
    from db import get_db
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "User not found"}), 404
        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@api_bp.route("/update-user", methods=["POST"])
@authenticate_token
def update_user():
    try:
        conn = get_db()
        cursor = conn.cursor()

        id = request.form.get("id")
        name = request.form.get("name")
        exp = request.form.get("exp")
        gym_id = request.form.get("gym_id")
        image_base64 = request.form.get("image")
        file = request.files.get("image")

        if not id or not name or not exp or not gym_id:
            return jsonify({"error": "Missing required fields"}), 400

        # default query & params
        query = """
            UPDATE users 
            SET name = %s, exp = %s, gym_id = %s
            WHERE id = %s
        """
        params = [name, exp, gym_id, id]

        # if file upload exists
        if file:
            image_data = file.read()
            query = """
                UPDATE users 
                SET name = %s, exp = %s, gym_id = %s, image = %s
                WHERE id = %s
            """
            params = [name, exp, gym_id, image_data, id]
        # if base64 image exists
        elif image_base64:
            matches = image_base64.split(";base64,")
            if len(matches) != 2:
                return jsonify({"error": "Invalid base64 image format"}), 400
            image_data = base64.b64decode(matches[1])
            query = """
                UPDATE users 
                SET name = %s, exp = %s, gym_id = %s, image = %s
                WHERE id = %s
            """
            params = [name, exp, gym_id, image_data, id]

        cursor.execute(query, params)
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "User not found"}), 404

        return jsonify({"message": "User updated successfully"}), 200

    except Exception as e:
        print("Error updating user:", e)
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()



# ---------------- LOGIN ----------------
@api_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    email, password = data.get("email"), data.get("password")
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM admin WHERE email = '{email}'")
    user = cursor.fetchone()
    
    
    if not user or not bcrypt.checkpw(password.encode(), user["password"].encode()):
        return jsonify({"error": "Invalid credentials"}), 401

    token = generate_access_token(user["id"])
    cursor.execute("SELECT * FROM gym WHERE admin_id = %s", (user["id"],))
    gym = cursor.fetchone()
    return jsonify({
        "userId": user["id"],
        "email": user["email"],
        "access_token": token,
        "gym_id": gym["id"] if gym else None,
        "gym_name": gym["name"] if gym else None,
        "token":token
    })
    


# ---------------- RESET PASSWORD ----------------
@api_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.json
    email, new_password, code = data.get("email"), data.get("password"), data.get("code")        
    hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()    
    

    conn = get_db()
    cursor = conn.cursor()    
    cursor.execute(f"UPDATE admin SET password='{hashed}' WHERE email='{email}' AND verify_code='{code}'")
    conn.commit()
    if cursor.rowcount == 0:

        return jsonify({"error": "User not found"}), 404
    cursor.execute(f"UPDATE admin SET verify_code=NULL WHERE email='{email}' AND verify_code='{code}'")
    conn.commit()
    return jsonify({"message": "Password updated successfully"}), 200


# --- Helper to generate random 6-digit code ---
def generate_verification_code(length=6):
    return ''.join(random.choices(string.digits, k=length))

# --- Flask route ---
@api_bp.route('/send-password-code', methods=['POST'])
def send_password_code():
    data = request.get_json()
    email = data.get('email')
    

    if not email:
        return jsonify({'error': 'Missing email or id'}), 400

    verification_code = generate_verification_code()

    # Optional: Twilio integration (commented out)
    """
    from twilio.rest import Client
    account_sid = 'YOUR_TWILIO_SID'
    auth_token = 'YOUR_TWILIO_TOKEN'
    client = Client(account_sid, auth_token)
    client.messages.create(
        body=f"Tu código es: {verification_code}",
        from_='+1234567890',  # Your Twilio number
        to='+521234567890'    # Recipient number
    )
    """

    try:
        conn = get_db()
        cursor = conn.cursor()
        query = """
            UPDATE `gyms`.`admin`
            SET `verify_code` = %s, `verify_code_exp` = DATE_ADD(NOW(), INTERVAL 2 HOUR)
            WHERE  email = %s;
        """
        cursor.execute(query, (verification_code, email))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"code": "is sent on email", "code":verification_code}), 200
    except Exception as err:
        print("Database error:", err)
        return jsonify({'error': f'Database error. {err}'}), 500