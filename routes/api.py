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
from PIL import Image
import io
import base64


api_bp = Blueprint("api", __name__)
@api_bp.route("/", methods=["GET"])
def index():
    return jsonify({"name":"api"})

# ---------------- USERS ----------------


@api_bp.route("/users", methods=["POST"])
def add_user():
    data = request.get_json()
    name = data.get("name")
    exp = data.get("exp")
    gym_id = data.get("gym_id")
    image_base64 = data.get("image")

    # Decode image from base64 to binary if provided
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




@api_bp.route("/entries/today/<int:gym_id>", methods=["GET"])
@authenticate_token
def get_today_entries(gym_id):
    from db import get_db

    limit = int(request.args.get("limit", 10))
    offset = int(request.args.get("offset", 0))

    query = """
        SELECT entries.*, users.name, users.exp, users.image, users.id AS user_id
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

        # Attach tiny thumbnail for each user entry
        for row in results:
            blob = row.get("image")

            if blob:
                img = Image.open(io.BytesIO(blob))

                # Small fast thumbnail
                img.thumbnail((48, 48))

                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=35)
                tiny_bytes = buffer.getvalue()

                row["image"] = base64.b64encode(tiny_bytes).decode("utf-8")
            else:
                row["image"] = None

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

        # check if the user ius not expired
        cursor.execute("SELECT id FROM users WHERE id = %s AND gym_id = %s AND exp >= NOW()", (user_id, gym_id))
        user = cursor.fetchone()
        if not user:
            return jsonify({"error": "exte usuaio esta expirado"}), 426

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


@api_bp.route("/biometrics/<int:user_id>", methods=["GET"])
@authenticate_token
def get_biometrics(user_id):
    from db import get_db

    query = """
        SELECT 
            biometrcs.id,
            biometrcs.user_id,
            biometrcs.peso,
            biometrcs.altura,
            biometrcs.cintura,
            biometrcs.bmg,
            biometrcs.date
        FROM biometrcs
        WHERE user_id = %s
        ORDER BY date DESC
    """

    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, (user_id,))
        biometrics = cursor.fetchall()
        return jsonify(biometrics), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


@api_bp.route("/biometrics", methods=["POST"])
@authenticate_token
def add_biometrics():
    from db import get_db

    data = request.get_json()

    required = ["user_id", "peso", "altura", "cintura", "bmg"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    query = """
        INSERT INTO biometrcs (user_id, peso, altura, cintura, bmg, date)
        VALUES (%s, %s, %s, %s, %s, NOW())
    """

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(query, (
            data["user_id"],
            data["peso"],
            data["altura"],
            data["cintura"],
            data["bmg"]
        ))
        conn.commit()

        return jsonify({"message": "Biometric data added successfully"}), 201

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


@api_bp.route("/gym/<int:gym_id>", methods=["PUT"])
@authenticate_token
def update_gym(gym_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        name = request.form.get("name")
        image_file = request.files.get("image")
        back_file = request.files.get("back")
        image_base64 = request.form.get("image")
        back_base64 = request.form.get("back")

        if not name and not image_file and not back_file and not image_base64 and not back_base64:
            return jsonify({"error": "Nothing to update"}), 400

        # Build dynamic query and params
        updates = []
        params = []

        if name:
            updates.append("name = %s")
            params.append(name)

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



@api_bp.route("/gym/<int:gym_id>", methods=["GET"])
@authenticate_token
def get_gym(gym_id):
    from db import get_db
    import base64

    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, admin_id, image, back FROM gym WHERE id = %s", (gym_id,))
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


@api_bp.route("/users/gym/<int:gym_id>", methods=["GET"])
@authenticate_token
def get_users_by_gym(gym_id):
    from db import get_db

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
            else:
                user["image"] = None

        return jsonify(users), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()



@api_bp.route("/users/<int:user_id>", methods=["PUT"])
@authenticate_token
def update_user(user_id):
    data = request.get_json()
    name = data.get("name")
    exp = data.get("exp")
    image_base64 = data.get("image")

    image_blob = None
    if image_base64:
        import base64
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




# ---------------- LOGIN ----------------
@api_bp.route("/login", methods=["POST"])
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