from flask import Blueprint, request, jsonify
from src.agents.orchestrator import intelligent_orchestrator
from src.utils.logger import log_event
import traceback

query_bp = Blueprint("query", __name__)

@query_bp.route("/query", methods=["POST"])
def query():
    try:
        payload = request.get_json()
        user_query = payload.get("query")
        if not user_query:
            return jsonify({"error": "El parámetro 'query' es obligatorio"}), 400
        
        log_event("Consulta recibida", {"query": user_query})
        response = intelligent_orchestrator(user_query)
        return jsonify({"response": response}), 200
    except Exception as e:
        log_event("Error en query endpoint", {"error": str(e), "trace": traceback.format_exc()})
        return jsonify({"error": "Error interno del servidor"}), 500
