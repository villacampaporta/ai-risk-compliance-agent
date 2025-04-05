import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
import os
from src.utils.logger import log_event

def generate_labels(df):
    """
    Simulate a fraud label based on a weighted score of selected features.
    This arbitrary function creates a binary target.
    """
    score = (
        df['amount'] / df['amount'].max() +
        df['ip_distance'] / df['ip_distance'].max() +
        (1 - df['merchant_risk']) +
        (1 / df['account_age']) +
        df['location_deviation'] / df['location_deviation'].max()
    )
    threshold = score.quantile(0.75)
    return (score > threshold).astype(int)

def train_model():
    data_file = "src/data/transactions_sample.csv"
    if not os.path.exists(data_file):
        print(f"Data file {data_file} does not exist. Generate transaction data first.")
        return

    df = pd.read_csv(data_file)
    df['is_fraud'] = generate_labels(df)
    
    feature_cols = [
        "amount", "ip_distance", "device_type_id", "time_of_day", 
        "tx_frequency", "merchant_risk", "account_age", "location_deviation"
    ]
    X = df[feature_cols]
    y = df['is_fraud']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    accuracy = model.score(X_test, y_test)
    log_event("Model training", {"accuracy": accuracy})
    print(f"Model trained with accuracy: {accuracy:.2f}")
    
    model_path = "src/model/fraud_model.pkl"
    joblib.dump(model, model_path)
    log_event("Model saved", {"model_path": model_path})
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train_model()
