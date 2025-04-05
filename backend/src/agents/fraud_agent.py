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
    """
    Extract features from a transaction dictionary to mimic real-world behavior.
    Expected fields: amount, ip_distance, device_type_id, time_of_day, tx_frequency,
    merchant_risk, account_age, and location_deviation.
    """
    try:
        amount = float(data.get("amount", 0))
        ip_distance = float(data.get("ip_distance", 0))
        device_type_id = int(data.get("device_type_id", 1))
        time_of_day = float(data.get("time_of_day", 12))
        tx_frequency = float(data.get("tx_frequency", 1))
        merchant_risk = float(data.get("merchant_risk", 0.5))
        account_age = float(data.get("account_age", 365))
        location_deviation = float(data.get("location_deviation", 0))
    except (ValueError, TypeError) as e:
        log_event("Feature extraction error", {"error": str(e)})
        raise ValueError("Invalid input data types for transaction features.")
        
    features = np.array([
        amount,
        ip_distance,
        device_type_id,
        time_of_day,
        tx_frequency,
        merchant_risk,
        account_age,
        location_deviation
    ]).reshape(1, -1)
    
    log_event("Extracted features", {"features": features.tolist()})
    return features

def fraud_agent(transaction: dict) -> dict:
    """
    Evaluate a transaction using the fraud detection model.
    Returns a dictionary with fraud probability and a risk level classification.
    """
    if model is None:
        return {"error": "Model not loaded"}
    
    try:
        features = extract_features(transaction)
        fraud_prob = model.predict_proba(features)[0][1]
        if fraud_prob > 0.75:
            risk_level = "high"
        elif fraud_prob > 0.5:
            risk_level = "medium"
        else:
            risk_level = "low"
            
        log_event("Fraud evaluation", {"fraud_probability": fraud_prob, "risk_level": risk_level})
        return {"fraud_probability": fraud_prob, "risk_level": risk_level}
    except Exception as e:
        log_event("Error evaluating transaction", {"error": str(e)})
        return {"error": "Failed to evaluate transaction"}

def simulate_transaction() -> dict:
    """
    Simulate a realistic transaction for testing purposes.
    """
    import random
    transaction = {
        "amount": round(random.uniform(1, 1000), 2),
        "ip_distance": round(random.uniform(0, 1000), 2),
        "device_type_id": random.choice([1, 2, 3]),
        "time_of_day": round(random.uniform(0, 23), 2),
        "tx_frequency": round(random.uniform(0, 10), 2),
        "merchant_risk": round(random.uniform(0, 1), 2),
        "account_age": round(random.uniform(10, 3650), 2),
        "location_deviation": round(random.uniform(0, 200), 2)
    }
    log_event("Simulated transaction", transaction)
    return transaction
