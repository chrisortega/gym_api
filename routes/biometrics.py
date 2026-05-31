"""
Routes for managing user biometrics data.
"""
from flask import Blueprint, request, jsonify
from db import get_db
from utils.auth import authenticate_token

biometrics_bp = Blueprint("biometrics", __name__)


@biometrics_bp.route("/biometrics/<int:user_id>", methods=["GET"])
@authenticate_token
def get_biometrics(user_id):
    """Retrieve biometric history for a specific user."""
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


@biometrics_bp.route("/biometrics", methods=["POST"])
@authenticate_token
def add_biometrics():
    """Add a new biometric entry for a user."""
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
        cursor.execute(
            query,
            (
                data["user_id"],
                data["peso"],
                data["altura"],
                data["cintura"],
                data["bmg"],
            ),
        )
        conn.commit()

        return jsonify({"message": "Biometric data added successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()
