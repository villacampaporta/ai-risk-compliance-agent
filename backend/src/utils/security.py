from functools import wraps
from flask import request, jsonify
import os

def require_api_key(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")
        expected_api_key = os.environ.get("API_KEY", "default-api-key")
        if not api_key or api_key != expected_api_key:
            return jsonify({"error": "Unauthorized access"}), 401
        return func(*args, **kwargs)
    return wrapper
