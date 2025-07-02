
import streamlit as st
import pandas as pd
from PIL import Image

# Logo
st.set_page_config(page_title="PUK AI Dashboard", layout="centered")

# Load local logo
st.image("logo.png", width=120)
st.title("PUK AI Dashboard")
st.markdown("**Prepared by Shvan**")

# --- Login System ---
def check_login(username, password):
    return username == "shvan" and password == "shvan1234"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if check_login(username, password):
            st.session_state.logged_in = True
            st.experimental_rerun()
        else:
            st.error("Invalid login credentials")
    st.stop()

# --- Main Dashboard ---
st.subheader("1. Paste Facebook Post Link")
fb_link = st.text_input("Enter Facebook post link here...")
if fb_link:
    st.warning("Auto-import from Facebook not enabled yet. Use manual file upload.")

st.subheader("2. Upload Facebook Comments/Post file (CSV, Excel, PDF)")
uploaded_file = st.file_uploader("Upload a file", type=["csv", "xlsx", "xls", "pdf"])
if uploaded_file:
    st.success("File uploaded.")
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.DataFrame({"Content": ["(PDF parsing not implemented in this demo)"]})
        st.dataframe(df.head())

        st.subheader("3. Kurdish Party Detection")
        parties = ["یەکێتی", "پارتی", "گۆڕان", "کۆمەڵ", "یەکگرتوو", "بەرەی گەل", "هەلوێست"]
        for party in parties:
            count = df.astype(str).apply(lambda row: row.str.contains(party)).sum().sum()
            st.write(f"{party}: {count} mentions")
    except Exception as e:
        st.error(f"Error reading file: {e}")
