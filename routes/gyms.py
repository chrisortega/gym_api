import base64
from flask import Blueprint, request, jsonify
from db import get_db
from utils.auth import authenticate_token

gyms_bp = Blueprint("gyms", __name__)


@gyms_bp.route("/gyms", methods=["GET"])
@authenticate_token
def get_gyms():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM gym")
    return jsonify(cursor.fetchall()), 200


@gyms_bp.route("/gym/<int:gym_id>", methods=["PUT"])
@authenticate_token
def update_gym(gym_id):
    if request.user.get("type") == "worker":
        return jsonify({"error": "Workers are not allowed to update the gym"}), 403
    try:
        conn = get_db()
        cursor = conn.cursor()
        name = request.form.get("name")
        image_file = request.files.get("image")
        back_file = request.files.get("back")
        image_base64 = request.form.get("image")
        back_base64 = request.form.get("back")
        capacity = request.form.get("capacity")

        if not name and not image_file and not back_file and not image_base64 and not back_base64:
            return jsonify({"error": "Nothing to update"}), 400

        # Build dynamic query and params
        updates = []
        params = []

        if name:
            updates.append("name = %s")
            params.append(name)

        if capacity:
            updates.append("capacity = %s")
            params.append(capacity)

        # Handle logo image (file)
        if image_file:
            image_data = image_file.read()
            updates.append("image = %s")
            params.append(image_data)
        elif image_base64:
            try:
                if ";base64," in image_base64:
                    image_data = base64.b64decode(image_base64.split(";base64,")[1])
                    updates.append("image = %s")
                    params.append(image_data)
            except Exception as e:
                return jsonify({"error": f"Invalid image base64: {str(e)}"}), 400

        # Handle background image (file)
        if back_file:
            back_data = back_file.read()
            updates.append("back = %s")
            params.append(back_data)
        elif back_base64:
            try:
                if ";base64," in back_base64:
                    back_data = base64.b64decode(back_base64.split(";base64,")[1])
                    updates.append("back = %s")
                    params.append(back_data)
            except Exception as e:
                return jsonify({"error": f"Invalid back base64: {str(e)}"}), 400

        if not updates:
            return jsonify({"error": "No valid fields to update"}), 400

        # Construct final query dynamically
        query = f"UPDATE gym SET {', '.join(updates)} WHERE id = %s"
        params.append(gym_id)

        cursor.execute(query, params)
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Gym not found"}), 404

        return jsonify({"message": "Gym updated successfully"}), 200

    except Exception as e:
        print("Error updating gym:", e)
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()



@gyms_bp.route("/gym/<int:gym_id>", methods=["GET"])
@authenticate_token
def get_gym(gym_id):        
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT *FROM gym WHERE id = %s", (gym_id,))
        gym = cursor.fetchone()

        if not gym:
            return jsonify({"error": "Gym not found"}), 404

        # Convert image (BLOB) to base64 if present
        if gym.get("image"):
            gym["image"] = base64.b64encode(gym["image"]).decode("utf-8")
        else:
            gym["image"] = None

     # Convert image (BLOB) to base64 if present
        if gym.get("back"):
            gym["back"] = base64.b64encode(gym["back"]).decode("utf-8")
        else:
            gym["back"] = None            

        return jsonify(gym), 200

    except Exception as e:
        print("Error loading gym:", e)
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@gyms_bp.route("/gym/<int:gym_id>/workers", methods=["GET"])
@authenticate_token
def get_gym_workers(gym_id):
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, email, username, phone FROM admin WHERE gym_id = %s AND type = 'worker' AND active = 1", (gym_id,))
        workers = cursor.fetchall()
        return jsonify(workers), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@gyms_bp.route("/gym/<int:gym_id>/workers", methods=["POST"])
@authenticate_token
def add_gym_worker(gym_id):
    if request.user.get("type") == "worker":
        return jsonify({"error": "Workers cannot add other workers"}), 403
    try:
        data = request.json
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
            
        import bcrypt
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Check if email exists
        cursor.execute("SELECT id FROM admin WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({"error": "Email already exists"}), 400
            
        cursor.execute(
            "INSERT INTO admin (name, email, password, gym_id, type, active) VALUES (%s, %s, %s, %s, 'worker', 1)",
            (name, email, hashed, gym_id)
        )
        conn.commit()
        
        return jsonify({"message": "Worker added successfully", "worker_id": cursor.lastrowid}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@gyms_bp.route("/gym/<int:gym_id>/workers/<int:worker_id>", methods=["DELETE"])
@authenticate_token
def remove_gym_worker(gym_id, worker_id):
    if request.user.get("type") == "worker":
        return jsonify({"error": "Workers cannot remove workers"}), 403
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE admin SET active = 0 WHERE id = %s AND gym_id = %s AND type = 'worker'", (worker_id, gym_id))
        conn.commit()
        
        if cursor.rowcount == 0:
            return jsonify({"error": "Worker not found"}), 404
            
        return jsonify({"message": "Worker removed successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

