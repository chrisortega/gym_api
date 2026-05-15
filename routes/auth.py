import random
import string
from flask import Blueprint, request, jsonify
from db import get_db
from utils.auth import generate_access_token
import bcrypt
from twilio.rest import Client
auth_bp = Blueprint("auth", __name__)


# ---------------- LOGIN ----------------
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    email, password = data.get("email"), data.get("password")
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"SELECT admin.password as password, admin.email as email, admin.id as user_id, gym.id as gym_id, gym.name as gym_name FROM admin inner join gym on admin.id = gym.admin_id WHERE email = '{email}' ")
    user = cursor.fetchone()
    
    
    if not user or not bcrypt.checkpw(password.encode(), user["password"].encode()):
        return jsonify({"error": "Invalid credentials"}), 401


    token = generate_access_token(user)
    return jsonify({
        "userId": user["user_id"],
        "email": user["email"],
        "access_token": token,
        "gym_id": user["gym_id"],
        "gym_name": user["gym_name"],
        "token":token
    })
    


# ---------------- RESET PASSWORD ----------------
@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.json
    email = data.get("email")
    new_password = data.get("password")
    code = data.get("code")

    # Validate required fields
    if not email or not new_password or not code:
        return jsonify({"error": "Missing email, password, or code"}), 400

    try:
        conn = get_db()
        cursor = conn.cursor()

        # Update password only if code matches AND has not expired
        hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
        cursor.execute(
            "UPDATE admin SET password = %s, verify_code = NULL, verify_code_exp = NULL "
            "WHERE email = %s AND verify_code = %s AND verify_code_exp >= NOW()",
            (hashed, email, code),
        )
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Invalid or expired verification code"}), 400

        return jsonify({"message": "Password updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# --- Helper to generate random 6-digit code ---
def generate_verification_code(length=6):
    return ''.join(random.choices(string.digits, k=length))

# --- Flask route ---
@auth_bp.route('/send-password-code', methods=['POST'])
def send_password_code():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'error': 'Missing email'}), 400

    verification_code = generate_verification_code()
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        query = """
            UPDATE `gyms`.`admin`
            SET `verify_code` = %s, `verify_code_exp` = DATE_ADD(NOW(), INTERVAL 2 HOUR)
            WHERE email = %s;
        """
        cursor.execute(query, (verification_code, email))
        
        # Capture how many rows were updated before committing
        rows_affected = cursor.rowcount
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Check if the email actually matched an existing user
        if rows_affected == 0:
            return jsonify({"error": f"No account found with email: {email}"}), 404

        # TODO: Send code via email/SMS instead of returning it in the response
        return jsonify({"message": "Verification code set successfully"}), 200
        
    except Exception as err:
        print("Database error:", err)
        return jsonify({'error': f'Database error. {err}'}), 500

