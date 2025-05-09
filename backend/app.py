import os
import logging
from flask import Flask, jsonify
from src.endpoints.transaction_endpoint import transaction_bp
from src.endpoints.query_endpoint import query_bp
from google.cloud import logging as cloud_logging
from src.config import Config

def create_app():
    app = Flask(__name__)
    
    # Load configuration from the Config class
    app.config.from_object(Config)
    
    # Initialize Google Cloud Logging for production-level logging
    try:
        client = cloud_logging.Client()
        client.setup_logging(log_level=logging.INFO)
        logging.info("Google Cloud Logging initialized successfully.")
    except Exception as e:
        logging.error(f"Error initializing Google Cloud Logging: {e}")
    
    # Register Blueprints with versioned URL prefixes
    app.register_blueprint(transaction_bp, url_prefix="/api")
    app.register_blueprint(query_bp, url_prefix="/api")
    
    # Health check endpoint
    @app.route("/health", methods=["GET"])
    def health_check():
        return jsonify({"status": "ok"}), 200

    # Global error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500

    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
