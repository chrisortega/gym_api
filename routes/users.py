import base64
import io
from flask import Blueprint, request, jsonify
from db import get_db
from utils.auth import authenticate_token
from PIL import Image

users_bp = Blueprint("users", __name__)


@users_bp.route("/users", methods=["POST"])
def add_user():
    data = request.get_json()
    name = data.get("name")
    exp = data.get("exp")
    gym_id = data.get("gym_id")
    image_base64 = data.get("image")

    # 
    # code image from base64 to binary if provided
    image_blob = None
    if image_base64:
        try:
            image_blob = base64.b64decode(image_base64)
        except Exception as e:
            return jsonify({"error": "Invalid image encoding", "details": str(e)}), 400

    conn = get_db()
    cursor = conn.cursor()

    if image_blob:
        cursor.execute(
            "INSERT INTO users (name, exp, gym_id, image) VALUES (%s, %s, %s, %s)",
            (name, exp, gym_id, image_blob),
        )
    else:
        cursor.execute(
            "INSERT INTO users (name, exp, gym_id) VALUES (%s, %s, %s)",
            (name, exp, gym_id),
        )

    conn.commit()
    return jsonify({"message": "User inserted successfully.", "id": cursor.lastrowid}), 200



@users_bp.route("/users", methods=["PUT"])
@authenticate_token
def update_user2():
    data = request.json
    user_id, name, exp = data.get("id"), data.get("name"), data.get("exp")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET name=%s, exp=%s WHERE id=%s", (name, exp, user_id))
    conn.commit()
    return jsonify({"message": "User updated successfully."}), 200

@users_bp.route("/users/<int:user_id>", methods=["GET"])
@authenticate_token
def get_user(user_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT users.exp, users.id,users.name, gym.name as gym_name, users.image  
        FROM users JOIN gym ON users.gym_id = gym.id
        WHERE users.id = %s
    """, (user_id,))    
    user = cursor.fetchone()
    
    if user.get("image"):
        user["image"] = base64.b64encode(user["image"]).decode("utf-8")
    else:
        user["image"] = None
    
    return jsonify(user or {}), 200


@users_bp.route("/users/gym/<int:gym_id>", methods=["GET"])
@authenticate_token
def get_users_by_gym(gym_id):
    query = """
        SELECT users.id, users.name, users.exp, users.image, gym.id AS gym_id
        FROM users
        JOIN gym ON users.gym_id = gym.id
        WHERE gym.id = %s
    """

    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, (gym_id,))
        users = cursor.fetchall()

        for user in users:
            blob = user.get("image")

            if blob:
                try:
                    # Convert blob → PIL image
                    img = Image.open(io.BytesIO(blob))

                    # Create tiny thumbnail
                    img.thumbnail((48, 48))   # small & fast

                    # Save back to bytes (compressed)
                    buffer = io.BytesIO()
                    img.save(buffer, format="JPEG", quality=35)
                    tiny_bytes = buffer.getvalue()

                    # Base64 encode thumbnail
                    user["image"] = base64.b64encode(tiny_bytes).decode("utf-8")
                except Exception:
                    user["image"] = None
            else:
                user["image"] = None

        return jsonify(users), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()



@users_bp.route("/users/<int:user_id>", methods=["PUT"])
@authenticate_token
def update_user(user_id):
    data = request.get_json()
    name = data.get("name")
    exp = data.get("exp")
    image_base64 = data.get("image")

    image_blob = None
    if image_base64:
        image_blob = base64.b64decode(image_base64)

    conn = get_db()
    cursor = conn.cursor()

    if image_blob:
        cursor.execute("""
            UPDATE users SET name=%s, exp=%s, image=%s WHERE id=%s
        """, (name, exp, image_blob, user_id))
    else:
        cursor.execute("""
            UPDATE users SET name=%s, exp=%s WHERE id=%s
        """, (name, exp, user_id))

    conn.commit()
    return jsonify({"message": "User updated successfully"})

@users_bp.route("/public/history/<int:user_id>", methods=["GET"])
def get_public_user_history(user_id):
    query_user = """
        SELECT users.id, users.name, users.exp, users.image, gym.name as gym_name
        FROM users 
        JOIN gym ON users.gym_id = gym.id
        WHERE users.id = %s
    """
    
    query_entries = """
        SELECT day 
        FROM entries 
        WHERE users_id = %s
        ORDER BY day DESC
    """
    
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        
        # Get user details
        cursor.execute(query_user, (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
            
        if user.get("image"):
            user["image"] = base64.b64encode(user["image"]).decode("utf-8")
        else:
            user["image"] = None
            
        # Get entries
        cursor.execute(query_entries, (user_id,))
        entries = cursor.fetchall()
        for row in entries:            
            if row.get("day"):                
                # Converts the raw datetime object to your desired string format
                row["day"] = row["day"].strftime("%Y-%m-%d %H:%M:%S")        
        user["entries"] = [entry["day"] for entry in entries]
        # Format the datetime objects safely in Python loop

        return jsonify(user), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
    finally:
        cursor.close()
        conn.close()
