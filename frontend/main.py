import streamlit as st
import requests
import json

# Backend configuration (override via .streamlit/secrets.toml or env vars)
BACKEND_URL = st.secrets.get("backend_url", "http://127.0.0.1:5000")
API_KEY     = st.secrets.get("API_KEY",     "default-api-key")

st.set_page_config(page_title="AI Risk & Compliance Agent", layout="wide")
st.title("AI Risk & Compliance Agent")
st.write("Interactively predict fraud risk or query compliance via our AI backend.")

# Sidebar: page selection
page = st.sidebar.selectbox("Choose a page", ["Transaction Prediction", "Compliance Query"])

if page == "Transaction Prediction":
    st.header("🕵️‍♂️ Transaction Prediction")
    with st.form("transaction_form"):
        amount             = st.number_input("Amount ($)", min_value=0.0, value=50.0, step=0.1)
        ip_distance        = st.number_input("IP Distance (km)", min_value=0.0, value=10.0, step=0.1)
        device_type_id     = st.selectbox("Device Type", ["Mobile (1)", "Desktop (2)", "Tablet (3)"])
        device_type_id     = int(device_type_id.split("(")[-1].strip(")"))
        time_of_day        = st.slider("Time of Day (hour)", 0, 23, 12)
        tx_frequency       = st.number_input("Transaction Frequency", min_value=0, value=1, step=1)
        merchant_risk      = st.slider("Merchant Risk (0–1)", 0.0, 1.0, 0.5, step=0.01)
        account_age        = st.number_input("Account Age (days)", min_value=0.0, value=365.0, step=1.0)
        location_deviation = st.number_input("Location Deviation (km)", min_value=0.0, value=5.0, step=0.1)
        submit_trans       = st.form_submit_button("Predict Fraud Risk")

    if submit_trans:
        transaction_payload = {
            "amount":             amount,
            "ip_distance":        ip_distance,
            "device_type_id":     device_type_id,
            "time_of_day":        time_of_day,
            "tx_frequency":       tx_frequency,
            "merchant_risk":      merchant_risk,
            "account_age":        account_age,
            "location_deviation": location_deviation
        }
        st.write("📤 Sending transaction payload:", transaction_payload)
        try:
            resp = requests.post(
                f"{BACKEND_URL}/api/predict_transaction",
                json=transaction_payload,
                headers={"X-API-Key": API_KEY},
                timeout=10
            )
            if resp.ok:
                st.success("✅ Prediction received:")
                st.json(resp.json())
            else:
                st.error(f"Error {resp.status_code}: {resp.text}")
        except Exception as e:
            st.error(f"Request failed: {e}")

elif page == "Compliance Query":
    st.header("📋 Compliance Query")
    with st.form("query_form"):
        query_text = st.text_area(
            "Enter your question:",
            value="¿Es esta transacción sospechosa?"
        )

        include_tx = st.checkbox("Include transaction data?", value=True)
        transaction = {}
        if include_tx:
            st.markdown("**Transaction data**")
            transaction = {
                "amount":             st.number_input("Amount ($)", min_value=0.0, value=1250.0, step=0.1, key="q_amt"),
                "ip_distance":        st.number_input("IP Distance (km)", min_value=0.0, value=350.0, step=0.1, key="q_ip"),
                "device_type_id":     int(st.selectbox("Device Type", ["Mobile (1)", "Desktop (2)", "Tablet (3)"], key="q_dev").split("(")[-1].strip(")")),
                "time_of_day":        st.slider("Time of Day (0–23)", 0, 23, 14, key="q_time"),
                "tx_frequency":       st.number_input("Transaction Frequency", min_value=0, value=2, step=1, key="q_freq"),
                "merchant_risk":      st.slider("Merchant Risk (0–1)", 0.0, 1.0, 0.3, step=0.01, key="q_mer"),
                "account_age":        st.number_input("Account Age (days)", min_value=0.0, value=45.0, step=1.0, key="q_acc"),
                "location_deviation": st.number_input("Location Deviation (km)", min_value=0.0, value=5.0, step=0.1, key="q_loc"),
            }

        submit_query = st.form_submit_button("Submit Query")

    if submit_query:
        payload = {"query": query_text}
        if include_tx:
            payload["transaction"] = transaction

        st.write("📤 Sending payload:", payload)
        try:
            resp = requests.post(
                f"{BACKEND_URL}/api/query",
                json=payload,
                headers={"X-API-Key": API_KEY},
                timeout=10
            )
            if resp.ok:
                st.success("✅ Response received:")
                st.json(resp.json())
            else:
                st.error(f"Error {resp.status_code}: {resp.text}")
        except Exception as e:
            st.error(f"Request failed: {e}")
