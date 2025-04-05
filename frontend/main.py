import streamlit as st
import requests
import json

# Retrieve backend URL and API key from secrets or environment variables
# Configure these values in your .streamlit/secrets.toml or environment
BACKEND_URL = st.secrets.get("backend_url", "http://localhost:8080")
API_KEY = st.secrets.get("API_KEY", "default-api-key")

st.set_page_config(page_title="AI Risk & Compliance Agent", layout="wide")
st.title("AI Risk & Compliance Agent")
st.write("This application allows you to predict fraud risk and query regulatory compliance information using our AI-powered backend.")

# Sidebar navigation
page = st.sidebar.selectbox("Choose a page", ["Transaction Prediction", "Compliance Query"])

if page == "Transaction Prediction":
    st.header("Transaction Prediction")
    st.write("Enter the details of the transaction below:")
    with st.form(key="transaction_form"):
        amount = st.number_input("Transaction Amount ($)", min_value=0.0, value=50.0, step=0.1)
        ip_distance = st.number_input("IP Distance (km)", min_value=0.0, value=10.0, step=0.1)
        device_type = st.selectbox("Device Type", options=["Mobile (1)", "Desktop (2)", "Tablet (3)"])
        device_type_id = int(device_type.split(" ")[-1].strip("()"))
        time_of_day = st.slider("Time of Day (hour)", 0, 23, 12)
        tx_frequency = st.number_input("Transaction Frequency", min_value=0, value=1, step=1)
        merchant_risk = st.slider("Merchant Risk (0-1)", 0.0, 1.0, 0.5, step=0.01)
        account_age = st.number_input("Account Age (days)", min_value=0.0, value=365.0, step=1.0)
        location_deviation = st.number_input("Location Deviation (km)", min_value=0.0, value=5.0, step=0.1)
        submit_trans = st.form_submit_button("Predict Fraud Risk")
    
    if submit_trans:
        # Construct the payload using real input data
        transaction_payload = {
            "amount": amount,
            "ip_distance": ip_distance,
            "device_type_id": device_type_id,
            "time_of_day": time_of_day,
            "tx_frequency": tx_frequency,
            "merchant_risk": merchant_risk,
            "account_age": account_age,
            "location_deviation": location_deviation
        }
        st.write("Sending transaction data:", transaction_payload)
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/predict_transaction",
                json=transaction_payload,
                headers={"X-API-Key": API_KEY},
                timeout=10
            )
            if response.status_code == 200:
                result = response.json()
                st.success("Prediction received!")
                st.json(result)
            else:
                st.error(f"Error: {response.status_code} {response.text}")
        except Exception as e:
            st.error(f"Exception during request: {e}")

elif page == "Compliance Query":
    st.header("Compliance Query")
    st.write("Enter your query regarding risk management or regulatory compliance:")
    with st.form(key="query_form"):
        query_text = st.text_area("Query", value="What are the latest compliance requirements for GDPR?")
        use_transaction = st.checkbox("Include transaction data in the query (optional)", value=False)
        transaction_data = {}
        if use_transaction:
            st.write("Enter transaction data:")
            trans_amount = st.number_input("Transaction Amount ($)", min_value=0.0, value=50.0, step=0.1, key="q_amount")
            trans_ip_distance = st.number_input("IP Distance (km)", min_value=0.0, value=10.0, step=0.1, key="q_ip_distance")
            trans_device = st.selectbox("Device Type", options=["Mobile (1)", "Desktop (2)", "Tablet (3)"], key="q_device")
            trans_device_id = int(trans_device.split(" ")[-1].strip("()"))
            trans_time = st.slider("Time of Day (hour)", 0, 23, 12, key="q_time")
            trans_tx_frequency = st.number_input("Transaction Frequency", min_value=0, value=1, step=1, key="q_frequency")
            trans_merchant_risk = st.slider("Merchant Risk (0-1)", 0.0, 1.0, 0.5, step=0.01, key="q_merchant_risk")
            trans_account_age = st.number_input("Account Age (days)", min_value=0.0, value=365.0, step=1.0, key="q_account_age")
            trans_location_deviation = st.number_input("Location Deviation (km)", min_value=0.0, value=5.0, step=0.1, key="q_location_deviation")
            transaction_data = {
                "amount": trans_amount,
                "ip_distance": trans_ip_distance,
                "device_type_id": trans_device_id,
                "time_of_day": trans_time,
                "tx_frequency": trans_tx_frequency,
                "merchant_risk": trans_merchant_risk,
                "account_age": trans_account_age,
                "location_deviation": trans_location_deviation
            }
        submit_query = st.form_submit_button("Submit Query")
    
    if submit_query:
        payload = {"query": query_text}
        if use_transaction:
            payload["transaction"] = transaction_data
        st.write("Sending query:", payload)
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/query",
                json=payload,
                headers={"X-API-Key": API_KEY},
                timeout=10
            )
            if response.status_code == 200:
                result = response.json()
                st.success("Query response received!")
                st.json(result)
            else:
                st.error(f"Error: {response.status_code} {response.text}")
        except Exception as e:
            st.error(f"Exception during request: {e}")
