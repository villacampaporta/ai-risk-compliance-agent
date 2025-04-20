import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_chat import message
import requests
from pathlib import Path

# --- Config & Caching ---
@st.cache_data(show_spinner=False)
def call_api(endpoint: str, payload: dict, api_key: str, base_url: str):
    """
    Send a POST to the backend and return (json, error_str).
    Cached to avoid repeated calls for identical inputs.
    """
    headers = {"X-API-Key": api_key, "Content-Type": "application/json"}
    try:
        resp = requests.post(f"{base_url}/api/{endpoint}", json=payload, headers=headers, timeout=60)
        if resp.ok:
            return resp.json(), None
        return None, f"{resp.status_code} - {resp.text}"
    except requests.exceptions.RequestException as e:
        return None, str(e)

# --- App Config ---
st.set_page_config(
    page_title="AI Risk & Compliance Agent",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Backend creds
BACKEND_URL = st.secrets.get("backend_url", "http://127.0.0.1:5000")
API_KEY     = st.secrets.get("API_KEY", "default-api-key")

# --- Sidebar Navigation with Option Menu ---
with st.sidebar:
    selected = option_menu(
        menu_title=None,
        options=["Transaction Prediction", "Compliance Query", "About"],
        icons=["activity", "question-circle", "info-circle"],
        menu_icon="cast",
        default_index=0,
    )

# --- Transaction Prediction ---
if selected == "Transaction Prediction":
    st.header("🕵️‍♂️ Transaction Prediction")
    with st.form("transaction_form", clear_on_submit=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            amount        = st.number_input("Amount ($)",         min_value=0.0, value=50.0)
            ip_distance   = st.number_input("IP Distance (km)",  min_value=0.0, value=10.0)
            time_of_day   = st.slider("Time of Day", 0, 23, 12)
        with c2:
            tx_frequency  = st.number_input("Tx Frequency",      min_value=0,   value=1)
            merchant_risk = st.slider("Merchant Risk (0–1)",     0.0, 1.0, 0.5)
            location_dev  = st.number_input("Location Deviation (km)", min_value=0.0, value=5.0)
        with c3:
            device_sel    = st.selectbox("Device Type", ["Mobile (1)", "Desktop (2)", "Tablet (3)"])
            device_type   = int(device_sel.split("(")[-1].strip(")"))
            account_age   = st.number_input("Account Age (days)", min_value=0.0, value=365.0)
        predict = st.form_submit_button("Predict Fraud Risk")

    if predict:
        payload = {
            "amount":             amount,
            "ip_distance":        ip_distance,
            "device_type_id":     device_type,
            "time_of_day":        time_of_day,
            "tx_frequency":       tx_frequency,
            "merchant_risk":      merchant_risk,
            "account_age":        account_age,
            "location_deviation": location_dev,
        }
        result, error = call_api("predict_transaction", payload, API_KEY, BACKEND_URL)
        if error:
            st.error(f"🚨 API Error: {error}")
        else:
            prob = result.get("fraud_probability", 0)
            level = result.get("risk_level", "unknown").capitalize()
            st.success("✅ Fraud Prediction Complete")
            colA, colB = st.columns([1,2])
            with colA:
                st.metric(label="Risk Level", value=level)
                st.metric(label="Probability", value=f"{prob:.1%}")
            with colB:
                st.progress(int(prob * 100))
            with st.expander("View Raw Response"):
                st.json(result)

# --- Compliance Query with Chat UI & Tabs ---
elif selected == "Compliance Query":
    st.header("📋 Compliance Query")
    tabs = st.tabs(["Q&A", "Transaction Data"])

    # Q&A Tab
    with tabs[0]:
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []  # list of (is_user, text)

        query = st.text_area("Enter your question:", height=120)
        send = st.button("Send Query")

        if send and query.strip():
            st.session_state.chat_history.append((True, query))
            payload = {"query": query}
            # include tx if user filled tab1 tx context? we check session
            if st.session_state.get("last_tx"):
                payload["transaction"] = st.session_state.last_tx
            resp, err = call_api("query", payload, API_KEY, BACKEND_URL)
            answer = resp.get("response") if resp else f"Error: {err}"
            st.session_state.chat_history.append((False, answer))

        # render chat
        for is_user, text in st.session_state.chat_history:
            message(text, is_user=is_user)

    # Transaction Data Tab
    with tabs[1]:
        st.markdown("**Provide context transaction data**")
        c1, c2 = st.columns(2)
        tx = {}
        with c1:
            tx["amount"]             = st.number_input("Amount ($)",         min_value=0.0, value=50.0, key="tx_amt")
            tx["ip_distance"]        = st.number_input("IP Distance (km)", min_value=0.0, value=10.0, key="tx_ip")
            sel = st.selectbox("Device Type", ["Mobile (1)", "Desktop (2)", "Tablet (3)"], key="tx_dev")
            tx["device_type_id"]     = int(sel.split("(")[-1].strip(")"))
            tx["tx_frequency"]       = st.number_input("Tx Frequency",      min_value=0,   value=1, key="tx_freq")
        with c2:
            tx["time_of_day"]        = st.slider("Time of Day", 0, 23, 12, key="tx_time")
            tx["merchant_risk"]      = st.slider("Merchant Risk (0–1)", 0.0, 1.0, 0.5, key="tx_mer")
            tx["account_age"]        = st.number_input("Account Age (days)", min_value=0.0, value=365.0, key="tx_acc")
            tx["location_deviation"] = st.number_input("Location Deviation (km)", min_value=0.0, value=5.0, key="tx_loc")
        if st.button("Save Transaction Context", key="save_tx"):
            st.session_state.last_tx = tx
            st.success("Transaction context saved ✅")

# --- About Page ---
elif selected == "About":
    st.header("ℹ️ About This App")
    st.markdown(
        """
        **AI Risk & Compliance Agent**  
        Version: 1.0.0  
        
        This interactive demo lets you predict transaction fraud risk and query compliance using our AI backend.  
        - **Tech stack:** Streamlit, Option‑Menu, Streamlit‑Chat, Python 3.10  
        - **Libraries:** `streamlit_option_menu`, `streamlit_chat`, `st.cache_data`  
        - **Author:** Your Team  
        """
    )
    if Path("README.md").exists():
        with open("README.md") as f:
            st.markdown(f.read())
