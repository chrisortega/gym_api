import base64
import io
from datetime import datetime
from flask import Blueprint, request, jsonify
from db import get_db
from utils.auth import authenticate_token
from PIL import Image

entries_bp = Blueprint("entries", __name__)


@entries_bp.route("/entries/today/<int:gym_id>", methods=["GET"])
@authenticate_token
def get_today_entries(gym_id):
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
                try:
                    img = Image.open(io.BytesIO(blob))

                    # Small fast thumbnail
                    img.thumbnail((48, 48))

                    buffer = io.BytesIO()
                    img.save(buffer, format="JPEG", quality=35)
                    tiny_bytes = buffer.getvalue()

                    row["image"] = base64.b64encode(tiny_bytes).decode("utf-8")
                except Exception:
                    row["image"] = None
            else:
                row["image"] = None

        return jsonify(results), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


@entries_bp.route("/entries/day/<int:gym_id>/<string:date_str>", methods=["GET"])
@authenticate_token
def get_entries_by_day(gym_id, date_str):
    query = """
        SELECT entries.*, users.name, users.id AS user_id
        FROM entries
        JOIN users ON entries.users_id = users.id
        WHERE DATE(day) = %s AND entries.gym_id = %s
        ORDER BY day DESC
    """

    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, (date_str, gym_id))
        results = cursor.fetchall()
        return jsonify(results), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()



@entries_bp.route("/entries", methods=["POST"])
@authenticate_token
def add_entry():
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

@entries_bp.route("/entries/user/<int:user_id>", methods=["GET"])
@authenticate_token
def get_entries_by_user(user_id):
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

@entries_bp.route("/entries/gym/<int:gym_id>/recent", methods=["GET"])
@authenticate_token
def get_recent_entries_by_gym(gym_id):
    limit = int(request.args.get("limit", 20))
    query = """
        SELECT entries.id, entries.day, users.name, users.id as user_id
        FROM entries
        JOIN users ON entries.users_id = users.id
        WHERE entries.gym_id = %s
        ORDER BY entries.day DESC
        LIMIT %s
    """
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, (gym_id, limit))
        results = cursor.fetchall()
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
