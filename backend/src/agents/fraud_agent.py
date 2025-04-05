import numpy as np
import joblib
import os
from src.utils.logger import log_event

# Path to the pretrained fraud detection model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "../model/fraud_model.pkl")
try:
    model = joblib.load(MODEL_PATH)
    log_event("Fraud model loaded", {"model_path": MODEL_PATH})
except Exception as e:
    log_event("Error loading fraud model", {"error": str(e)})
    model = None

def extract_features(data: dict):
    try:
        amount = float(data.get("amount", 0))
        ip_distance = float(data.get("ip_distance", 0))
        device_type_id = int(data.get("device_type_id", 1))
        time_of_day = float(data.get("time_of_day", 12))
        tx_frequency = float(data.get("tx_frequency", 1))
    except (ValueError, TypeError) as e:
        log_event("Feature extraction error", {"error": str(e)})
        raise ValueError("Invalid input data types for transaction features.")
        
    return np.array([amount, ip_distance, device_type_id, time_of_day, tx_frequency]).reshape(1, -1)

def fraud_agent(transaction: dict) -> dict:
    if model is None:
        return {"error": "Model not loaded"}
    
    try:
        features = extract_features(transaction)
        fraud_prob = model.predict_proba(features)[0][1]
        # Define risk level based on probability thresholds
        if fraud_prob > 0.7:
            risk_level = "high"
        elif fraud_prob > 0.4:
            risk_level = "medium"
        else:
            risk_level = "low"
            
        return {"fraud_probability": fraud_prob, "risk_level": risk_level}
    except Exception as e:
        log_event("Error evaluating transaction", {"error": str(e)})
        return {"error": "Failed to evaluate transaction"}
