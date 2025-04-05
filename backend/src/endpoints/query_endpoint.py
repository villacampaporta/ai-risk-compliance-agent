import traceback
from flask import Blueprint, request, jsonify
from src.agents.orchestrator import intelligent_orchestrator
from src.utils.logger import log_event
from src.utils.security import require_api_key

query_bp = Blueprint("query", __name__)

@query_bp.route("/query", methods=["POST"])
@require_api_key
def query():
    try:
        payload = request.get_json()
        user_query = payload.get("query")
        if not user_query:
            return jsonify({"error": "The 'query' parameter is required"}), 400
        
        log_event("Query received", {"query": user_query})
        response = intelligent_orchestrator(user_query)
        return jsonify({"response": response}), 200
    except Exception as e:
        log_event("Error in query endpoint", {"error": str(e), "trace": traceback.format_exc()})
        return jsonify({"error": "Internal server error"}), 500
