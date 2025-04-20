# frontend/app.py
import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_chat import message
import requests
import pandas as pd
import math
from datetime import datetime, date
from pathlib import Path
from geopy.geocoders import Nominatim

# --- Page Configuration (must be first) ---
st.set_page_config(
    page_title="AI Risk & Compliance Agent",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CSS Styling for Professional Theme & Chat Bubbles ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
    html, body, [class*=\"css\"] { font-family: 'Roboto', sans-serif; background-color: #f7f9fc; color: #333; }
    h1 { color: #00447c !important; font-size: 2.75rem !important; font-weight: 700 !important; margin-bottom: 0.5rem; }
    p.subtitle { font-size: 1rem; color: #555; margin-bottom: 1rem; }
    .user-bubble { background-color: #0072ce; color: #fff; padding: 10px; border-radius: 10px; text-align: right; margin: 5px 0; }
    .ai-bubble   { background-color: #e0e0e0; color: #333; padding: 10px; border-radius: 10px; text-align: left; margin: 5px 0; }
    .stButton>button { background-color: #0072ce !important; color: #fff !important; border-radius: 8px !important; padding: 0.6rem 1.2rem !important; font-weight: 600 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Header ---
st.markdown("<h1>Financial Risk & Compliance Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Real-time fraud detection & regulatory compliance assistant.</p>", unsafe_allow_html=True)

# --- Backend Credentials ---
BACKEND_URL = st.secrets.get("backend_url", "http://127.0.0.1:5000")
API_KEY     = st.secrets.get("API_KEY",     "default-api-key")

# --- Geolocator ---
geolocator = Nominatim(user_agent="risk_compliance_app")

@st.cache_data
def geocode_address(address: str):
    try:
        loc = geolocator.geocode(address)
        return loc.latitude, loc.longitude
    except:
        return None, None

# --- Haversine Distance Function ---
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# --- API Helper ---
@st.cache_data(show_spinner=False)
def call_api(endpoint: str, payload: dict):
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    try:
        resp = requests.post(f"{BACKEND_URL}/api/{endpoint}", json=payload, headers=headers, timeout=60)
        if resp.ok:
            return resp.json(), None
        return None, f"{resp.status_code} - {resp.text}"
    except requests.exceptions.RequestException as e:
        return None, str(e)

# --- Sidebar Navigation ---
with st.sidebar:
    selected = option_menu(
        menu_title="Navigation",
        options=["Assistant", "About"],
        icons=["question-circle", "info-circle"],
        menu_icon="shield-check",
        default_index=0,
    )

# --- Compliance Query Page ---
if selected == "Assistant":
    st.header("📋 Ask our assistant")
    st.info("Use the Q&A tab to ask compliance questions. Provide transaction context in the Context tab.")

    # Initialize chat with greeting
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [(False, "Hi! What can I assist you with?")]

    tabs = st.tabs(["Q&A", "Context"])

    # Q&A Tab
    with tabs[0]:
        with st.form("qa_form", clear_on_submit=True):
            user_msg = st.text_input(
                "Your question:",
                key="input_q",
                placeholder="e.g. What are the latest GDPR requirements?"
            )
            send     = st.form_submit_button("Send")
        if send and user_msg:
            st.session_state.chat_history.append((True, user_msg))
            payload = {"query": user_msg}
            if tx := st.session_state.get("tx_context"):
                payload["transaction"] = tx
            resp, err = call_api("query", payload)
            answer = resp.get("response") if resp else f"Error: {err}"
            st.session_state.chat_history.append((False, answer))

        # for idx, (is_user, msg) in enumerate(st.session_state.chat_history):
        #     cls = "user-bubble" if is_user else "ai-bubble"
        #     st.markdown(f"<div class='{cls}'>{msg}</div>", unsafe_allow_html=True)

        for idx, (is_user, msg) in enumerate(st.session_state.chat_history):
            avatar = "shapes" if is_user else "shapes"
            seed = "Felix" if is_user else "assistant"
            message(
                msg,
                is_user=is_user,
                key=f"msg_{idx}",
                avatar_style=avatar,
                seed=seed
            )

    # Context Tab
    with tabs[1]:
        st.subheader("Transaction Context")
        st.markdown("Provide intuitive inputs. Addresses will be geocoded.")
        tx = None
        uploaded = st.file_uploader(
            "Upload CSV of model features",
            type=["csv"],
            help="CSV must have raw features: amount, ip_distance, device_type_id, time_of_day, tx_frequency, merchant_risk, account_age, location_deviation"
        )
        if uploaded:
            df = pd.read_csv(uploaded)
            st.dataframe(df)
            idx = st.selectbox("Select row index", df.index, key="csv_idx")
            tx = df.loc[idx].to_dict()
            st.success(f"Loaded transaction from row {idx}")
        else:
            st.markdown("**Or enter details manually:**")
            c1, c2 = st.columns(2)
            with c1:
                amount      = st.number_input("Amount (USD)", 0.01, 1e6, 50.0, key="ctx_amt")
                origin_addr = st.text_input("Transaction Origin (city or address)", key="ctx_origin")
                merchant_addr= st.text_input("Merchant Location (city or address)", key="ctx_merchant")
                tx_freq     = st.number_input("Transactions in Last 24h", 0, 1000, 1, key="ctx_freq")
            with c2:
                merchant_risk = st.slider("Merchant Risk (0–1)", 0.0, 1.0, 0.5, key="ctx_mer")
                acct_date     = st.date_input("Account Creation Date", value=date.today().replace(year=date.today().year-1), key="ctx_acc")
            # Geocode addresses
            orig_lat, orig_lon = geocode_address(origin_addr) if origin_addr else (None, None)
            mer_lat, mer_lon   = geocode_address(merchant_addr) if merchant_addr else (None, None)
            if orig_lat and mer_lat:
                dist_km = haversine(orig_lat, orig_lon, mer_lat, mer_lon)
            else:
                dist_km = None
            time_sel      = st.time_input("Transaction Time", value=datetime.now().time(), key="ctx_time")
            time_of_day   = round(time_sel.hour + time_sel.minute/60, 2)
            account_age   = (date.today() - acct_date).days
            device_sel    = st.selectbox("Device Type", ["Mobile Phone", "Desktop Computer", "Tablet Device"], key="ctx_dev")
            device_map    = {"Mobile Phone":1, "Desktop Computer":2, "Tablet Device":3}
            tx = {
                "amount":             round(amount,2),
                "ip_distance":        round(dist_km,2) if dist_km else 0,
                "device_type_id":     device_map.get(device_sel,1),
                "time_of_day":        time_of_day,
                "tx_frequency":       tx_freq,
                "merchant_risk":      merchant_risk,
                "account_age":        account_age,
                "location_deviation": round(dist_km,2) if dist_km else 0,
            }
        if st.button("Save Context", key="save_ctx"):
            if tx:
                st.session_state.tx_context = tx
                st.success("✅ Transaction context saved.")
            else:
                st.error("No transaction context to save.")

# --- About Page ---
elif selected == "About":
    st.header("ℹ️ About Financial Risk & Compliance assistant")
    readme_path = Path(__file__).resolve().parent / 'USER_GUIDE.md'
    if not readme_path.exists():
        md_path = Path.cwd() / "USER_GUIDE.md"
    if readme_path.exists():
        st.markdown(readme_path.read_text(encoding="utf-8"), unsafe_allow_html=True)
    else:
        st.write("**Financial Risk & Compliance Agent:** Streamline fraud detection & compliance.")
    st.write("© 2025 ICAI Consultants. All rights reserved.")