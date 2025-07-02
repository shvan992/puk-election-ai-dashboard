
import streamlit as st
import pandas as pd
import uuid
from PIL import Image

st.set_page_config(page_title="PUK AI Dashboard", layout="centered")

# Load logo
st.image("logo.png", width=120)
st.title("PUK AI Dashboard")

# Language Selector
lang = st.selectbox("🌐 Language / زمان", ["English", "کوردی", "عربي"])

# Login form
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("### Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        show_password = st.checkbox("Show password")
        if show_password:
            st.text(f"Password: {password}")
        submitted = st.form_submit_button("Login")
        if submitted:
            if username == "shvan" and password == "shvan1234":
                st.session_state.logged_in = True
                st.experimental_rerun()
            else:
                st.error("Invalid username or password.")
    st.stop()

# After login
st.markdown("### Welcome, Shvan!")
st.markdown("**Prepared by Shvan**")

st.subheader("1. Paste Facebook Post Link (Auto Convert to CSV)")
fb_link = st.text_input("Paste Facebook post link")
if fb_link:
    st.info("Simulating Facebook data extraction...")
    comments = [
        "پارتی دەبێت لەسەر هەڵوێستی خۆی بیستووری بکات",
        "من پشتیوانی یەکێتی دەکەم",
        "بەرەی گەل و هەلوێست دەبن جلوبەرگی نوێ",
        "گۆڕان هەستی نوێیان پێشکەش کردووە",
        "یەکگرتوو گرنگە لە هەرێم"
    ]
    df = pd.DataFrame({"Comment": comments})
    csv_file = f"{uuid.uuid4().hex[:6]}_comments.csv"
    df.to_csv(csv_file, index=False)
    st.success(f"Facebook post data converted to {csv_file}")
    st.dataframe(df)

    st.subheader("Kurdish Party Detection")
    parties = ["یەکێتی", "پارتی", "گۆڕان", "کۆمەڵ", "یەکگرتوو", "بەرەی گەل", "هەلوێست"]
    for party in parties:
        count = df.astype(str).apply(lambda row: row.str.contains(party)).sum().sum()
        st.write(f"{party}: {count} mentions")

st.subheader("2. Or Upload Comments/Post File (CSV, Excel, PDF)")
uploaded_file = st.file_uploader("Upload file", type=["csv", "xlsx", "xls", "pdf"])
if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.DataFrame({"Content": ["(PDF parsing not supported in this version)"]})
        st.success("File uploaded successfully.")
        st.dataframe(df)

        st.subheader("Kurdish Party Detection")
        for party in parties:
            count = df.astype(str).apply(lambda row: row.str.contains(party)).sum().sum()
            st.write(f"{party}: {count} mentions")
    except Exception as e:
        st.error(f"Error reading file: {e}")
