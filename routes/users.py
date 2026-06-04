"""
Routes for managing regular gym users.
"""
import base64
import io
from flask import Blueprint, request, jsonify
from db import get_db
from utils.auth import authenticate_token
from PIL import Image
from utils.s3_helper import upload_base64_to_s3, get_presigned_url

users_bp = Blueprint("users", __name__)


@users_bp.route("/users", methods=["POST"])
def add_user():
    """Create a new user in the gym."""
    data = request.get_json()
    name = data.get("name")
    exp = data.get("exp")
    gym_id = data.get("gym_id")
    image_base64 = data.get("image")

    # upload image to S3 if provided
    image_url = None
    if image_base64:
        try:
            image_url = upload_base64_to_s3(image_base64, folder="users")
        except Exception as e:
            return jsonify({"error": "Failed to upload image", "details": str(e)}), 400

    conn = get_db()
    cursor = conn.cursor()

    if image_url:
        cursor.execute(
            "INSERT INTO users (name, exp, gym_id, image) VALUES (%s, %s, %s, %s)",
            (name, exp, gym_id, image_url),
        )
    else:
        cursor.execute(
            "INSERT INTO users (name, exp, gym_id) VALUES (%s, %s, %s)",
            (name, exp, gym_id),
        )

    conn.commit()
    return jsonify(
        {"message": "User inserted successfully.", "id": cursor.lastrowid}
    ), 200


@users_bp.route("/users", methods=["PUT"])
@authenticate_token
def update_user2():
    """Update a user's name and expiration date (alternative endpoint)."""
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
    """Retrieve detailed information about a specific user."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT users.exp, users.id,users.name, gym.name as gym_name, users.image  
        FROM users JOIN gym ON users.gym_id = gym.id
        WHERE users.id = %s
    """,
        (user_id,),
    )
    user = cursor.fetchone()

    if user:
        user["image"] = get_presigned_url(user.get("image"))

    return jsonify(user or {}), 200


@users_bp.route("/users/gym/<int:gym_id>", methods=["GET"])
@authenticate_token
def get_users_by_gym(gym_id):
    """Retrieve all users associated with a specific gym."""
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
            user["image"] = get_presigned_url(user.get("image"))

        return jsonify(users), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


@users_bp.route("/users/<int:user_id>", methods=["PUT"])
@authenticate_token
def update_user(user_id):
    """Update a user's profile information including their image."""
    data = request.get_json()
    name = data.get("name")
    exp = data.get("exp")
    image_base64 = data.get("image")

    image_url = None
    if image_base64:
        image_url = upload_base64_to_s3(image_base64, folder="users")

    conn = get_db()
    cursor = conn.cursor()

    if image_url:
        cursor.execute(
            """
            UPDATE users SET name=%s, exp=%s, image=%s WHERE id=%s
        """,
            (name, exp, image_url, user_id),
        )
    else:
        cursor.execute(
            """
            UPDATE users SET name=%s, exp=%s WHERE id=%s
        """,
            (name, exp, user_id),
        )

    conn.commit()
    return jsonify({"message": "User updated successfully"})


@users_bp.route("/public/history/<int:user_id>", methods=["GET"])
def get_public_user_history(user_id):
    """Retrieve a public view of a user's entry history."""
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

        user["image"] = get_presigned_url(user.get("image"))

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
