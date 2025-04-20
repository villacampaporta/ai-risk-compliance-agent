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
        payload = request.get_json()
        txn = payload.get("transaction")

        if not txn:
            return jsonify({"error": "No input data provided"}), 400

        log_event("Transaction received", txn)
        result = fraud_agent(txn)
        return jsonify(result), 200
    except Exception as e:
        log_event("Error in predict_transaction", {"error": str(e), "trace": traceback.format_exc()})
        return jsonify({"error": "Internal server error"}), 500
