from flask import Blueprint, request, jsonify
from src.agents.fraud_agent import fraud_agent
from src.utils.logger import log_event
import traceback

transaction_bp = Blueprint("transaction", __name__)

@transaction_bp.route("/predict_transaction", methods=["POST"])
def predict_transaction():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No se proporcionaron datos de entrada"}), 400

        log_event("Transacción recibida", data)
        result = fraud_agent(data)
        return jsonify(result), 200
    except Exception as e:
        log_event("Error en predict_transaction", {"error": str(e), "trace": traceback.format_exc()})
        return jsonify({"error": "Error interno del servidor"}), 500

