"""
Routes for managing gym entries.
"""
import base64
import io
from flask import Blueprint, request, jsonify
from db import get_db
from utils.auth import authenticate_token
from PIL import Image



entries_bp = Blueprint("entries", __name__)


@entries_bp.route("/entries/today/<int:gym_id>", methods=["GET"])
@authenticate_token
def get_today_entries(gym_id):
    """Retrieve all entries for a specific gym for today."""
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
    """Retrieve entries for a specific gym on a specific day."""
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


@entries_bp.route("/entries/range/<int:gym_id>", methods=["GET"])
@authenticate_token
def get_entries_by_range(gym_id):
    """Retrieve entries for a specific gym within a date range."""
    start_date = request.args.get("start")
    end_date = request.args.get("end")
    if not start_date or not end_date:
        return jsonify({"error": "Missing start or end date"}), 400

    query = """
        SELECT entries.*, users.name, users.id AS user_id
        FROM entries
        JOIN users ON entries.users_id = users.id
        WHERE DATE(day) BETWEEN %s AND %s AND entries.gym_id = %s
        ORDER BY day DESC
    """

    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, (start_date, end_date, gym_id))
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
    """Add a new gym entry for a user if they are valid and not expired."""
    data = request.json
    user_id = data.get("user_id")
    gym_id = data.get("gym_id")

    if not user_id or not gym_id:
        return jsonify({"error": "Missing user_id or gym_id"}), 400

    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        # Check if user belongs to this gym
        cursor.execute(
            "SELECT id FROM users WHERE id = %s AND gym_id = %s", (user_id, gym_id)
        )
        user = cursor.fetchone()
        if not user:
            return jsonify({"error": "Este usuario no está en este gimnasio"}), 426

        # 2. Check if the user is not expired
        cursor.execute(
            "SELECT id FROM users WHERE id = %s AND gym_id = %s AND exp >= CURDATE()",
            (user_id, gym_id),
        )
        user = cursor.fetchone()
        if not user:
            return jsonify({"error": "Usuario expirado"}), 426

        # 3. Insert entry using database NOW()
        query = "INSERT INTO entries (users_id, gym_id, day) VALUES (%s, %s, NOW())"
        cursor.execute(query, (user_id, gym_id))
        new_entry_id = cursor.lastrowid
        conn.commit()
        
        cursor.execute("SELECT day FROM entries WHERE id = %s", (new_entry_id,))
        entry_row = cursor.fetchone()
        entry_date_str = entry_row["day"].strftime("%Y-%m-%d %H:%M:%S") if entry_row and entry_row.get("day") else None

        return jsonify(
            {
                "message": "Entry registered successfully",
                "id": new_entry_id,
                "user_id": user_id,
                "entry_date": entry_date_str,
            }
        ), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@entries_bp.route("/entries/user/<int:user_id>", methods=["GET"])
@authenticate_token
def get_entries_by_user(user_id):
    """Retrieve all entries for a specific user."""
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
    """Retrieve the most recent entries for a specific gym."""
    limit = int(request.args.get("limit", 20))

    # Removed DATE_FORMAT completely so there are exactly two %s symbols
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

        # Format the datetime objects safely in Python loop
        for row in results:
            if row.get("day"):
                # Converts the raw datetime object to your desired string format
                row["day"] = row["day"].strftime("%Y-%m-%d %H:%M:%S")

        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
