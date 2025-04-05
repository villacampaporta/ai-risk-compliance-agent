from flask import Flask, jsonify
from src.endpoints.transaction_endpoint import transaction_bp
from src.endpoints.query_endpoint import query_bp
from google.cloud import logging as cloud_logging
import os
import logging

def create_app():
    app = Flask(__name__)
    
    # Configuración de variables de entorno (DEBUG, etc.)
    app.config["DEBUG"] = os.environ.get("DEBUG", "False") == "True"
    
    # Inicialización del Logging de GCP
    try:
        client = cloud_logging.Client()
        client.setup_logging(log_level=logging.INFO)
        logging.info("Logging de GCP inicializado correctamente.")
    except Exception as e:
        logging.error(f"Error al inicializar el logging de GCP: {e}")
    
    # Registro de Blueprints con prefijo de versión (por ejemplo, /api)
    app.register_blueprint(transaction_bp, url_prefix="/api")
    app.register_blueprint(query_bp, url_prefix="/api")
    
    # Endpoint de salud
    @app.route("/health", methods=["GET"])
    def health_check():
        return jsonify({"status": "ok"}), 200
    
    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)