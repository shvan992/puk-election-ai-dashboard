
import streamlit as st
import pandas as pd

# --- Authentication ---
def check_login(username, password):
    return username == "shvan" and password == "shvan1234"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/Flag_of_PUK.svg/2560px-Flag_of_PUK.svg.png", width=200)
    st.title("PUK AI Dashboard")
    st.write("Please log in to continue.")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if check_login(username, password):
            st.session_state.logged_in = True
            st.experimental_rerun()
        else:
            st.error("Invalid login credentials.")
    st.stop()

# --- Main App After Login ---
st.title("PUK Election AI Dashboard")

st.subheader("1. Paste Facebook Post Link")
fb_link = st.text_input("Enter Facebook post link here...")
if fb_link:
    st.warning("Facebook link auto-import not connected yet. Please manually upload post/comments for now.")

st.subheader("2. Upload Facebook Comments/Post file (CSV, Excel, PDF)")
uploaded_file = st.file_uploader("Upload a file", type=["csv", "xlsx", "xls", "pdf"])
if uploaded_file:
    st.success("File uploaded successfully.")
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.DataFrame({"Content": ["(PDF parsing not yet implemented)"]})

    st.write("Data Preview:")
    st.dataframe(df.head())

    st.subheader("3. Kurdish Party Detection")
    parties = ["یەکێتی", "پارتی", "گۆڕان", "کۆمەڵ", "یەکگرتوو", "بەرەی گەل", "هەلوێست"]
    for party in parties:
        count = df.astype(str).apply(lambda row: row.str.contains(party)).sum().sum()
        st.write(f"{party}: {count} mentions")
