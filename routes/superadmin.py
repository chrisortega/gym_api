import bcrypt
from flask import Blueprint, request, jsonify
from db import get_db
from utils.auth import authenticate_token

superadmin_bp = Blueprint("superadmin", __name__)

# Basic middleware to check if super admin
def is_super_admin(user_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT username FROM admin WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user and user.get("username") is not None

@superadmin_bp.route("/superadmin/gyms", methods=["GET"])
@authenticate_token
def get_all_gyms():
    user_id = request.user.get("user_id") or request.user.get("id") # JWT payload has user_id
    if not is_super_admin(user_id):
        return jsonify({"error": "Unauthorized"}), 403
        
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT gym.id as gym_id, gym.name as gym_name, admin.id as admin_id, admin.email as admin_email
        FROM gym
        JOIN admin ON gym.admin_id = admin.id
    """
    cursor.execute(query)
    gyms = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return jsonify(gyms), 200

@superadmin_bp.route("/superadmin/gyms", methods=["POST"])
@authenticate_token
def add_gym_and_admin():
    user_id = request.user.get("user_id") or request.user.get("id")
    if not is_super_admin(user_id):
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    gym_name = data.get("gym_name")
    admin_email = data.get("admin_email")
    admin_password = data.get("admin_password")
    
    if not gym_name or not admin_email or not admin_password:
        return jsonify({"error": "Missing fields"}), 400

    hashed_pw = bcrypt.hashpw(admin_password.encode(), bcrypt.gensalt()).decode()

    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Create admin
        cursor.execute("INSERT INTO admin (email, password) VALUES (%s, %s)", (admin_email, hashed_pw))
        new_admin_id = cursor.lastrowid
        
        # Create gym
        cursor.execute("INSERT INTO gym (name, admin_id) VALUES (%s, %s)", (gym_name, new_admin_id))
        
        conn.commit()
        return jsonify({"message": "Gym and admin created successfully"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@superadmin_bp.route("/superadmin/admins/<int:admin_id>", methods=["PUT"])
@authenticate_token
def update_admin_email(admin_id):
    user_id = request.user.get("user_id") or request.user.get("id")
    if not is_super_admin(user_id):
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    new_email = data.get("email")
    if not new_email:
        return jsonify({"error": "Missing email"}), 400

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE admin SET email = %s WHERE id = %s AND username IS NULL", (new_email, admin_id))
        conn.commit()
        return jsonify({"message": "Admin email updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@superadmin_bp.route("/superadmin/gyms/<int:gym_id>", methods=["DELETE"])
@authenticate_token
def delete_gym(gym_id):
    user_id = request.user.get("user_id") or request.user.get("id")
    if not is_super_admin(user_id):
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM gym WHERE id = %s", (gym_id,))
        conn.commit()
        return jsonify({"message": "Gym deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
