import traceback
from flask import Blueprint, request, jsonify
from src.agents.fraud_agent import fraud_agent
from src.utils.logger import log_event
from src.utils.security import require_api_key

transaction_bp = Blueprint("transaction", __name__)

@transaction_bp.route("/predict_transaction", methods=["POST"])
@require_api_key
def predict_transaction():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No input data provided"}), 400

        log_event("Transaction received", data)
        result = fraud_agent(data)
        return jsonify(result), 200
    except Exception as e:
        log_event("Error in predict_transaction", {"error": str(e), "trace": traceback.format_exc()})
        return jsonify({"error": "Internal server error"}), 500
