
import streamlit as st
import pandas as pd
import requests
import os

st.set_page_config(page_title="PUK Election AI Dashboard", layout="wide")
st.markdown("""<h1 style='text-align: center;'>PUK AI Dashboard</h1>""", unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.image("puk_logo.png", width=100)
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    lang = st.selectbox("Language", ["English", "Kurdish", "Arabic"])
    if st.button("Login"):
        if username == "shvan" and password == "shvan1234":
            st.session_state.logged_in = True
        else:
            st.error("Invalid credentials")

def analyze_csv(file):
    df = pd.read_csv(file)
    st.write("Sample of uploaded data:")
    st.dataframe(df.head())
    st.success("CSV analysis completed (placeholder)")

def fetch_comments_from_facebook(post_id, access_token):
    url = f"https://graph.facebook.com/v18.0/{post_id}/comments?access_token={access_token}&limit=10000"
    comments = []
    while url:
        res = requests.get(url).json()
        comments += [c['message'] for c in res.get('data', []) if 'message' in c]
        url = res.get('paging', {}).get('next')
    return comments

def extract_post_id(link):
    import re
    if "posts/" in link:
        return link.split("posts/")[1].split("/")[0]
    elif "photo?fbid=" in link:
        return link.split("photo?fbid=")[1].split("&")[0]
    elif "/videos/" in link:
        return link.split("/videos/")[1].split("/")[0]
    elif "story_fbid=" in link:
        return link.split("story_fbid=")[1].split("&")[0]
    elif "/share/" in link:
        return None
    return None

if not st.session_state.logged_in:
    login()
else:
    st.sidebar.success("Logged in as: shvan")
    st.sidebar.image("puk_logo.png", width=80)
    st.sidebar.write("Prepared by Shvan Qaraman")

    st.subheader("Paste Facebook Post Link")
    fb_link = st.text_input("Facebook Post URL")
    access_token = "PASTE_YOUR_ACCESS_TOKEN_HERE"  # Replace with actual token

    if st.button("Fetch & Convert to CSV"):
        post_id = extract_post_id(fb_link)
        if post_id:
            comments = fetch_comments_from_facebook(post_id, access_token)
            df = pd.DataFrame(comments, columns=["Comment"])
            df.to_csv("facebook_comments.csv", index=False)
            st.success("Comments saved to facebook_comments.csv")
            st.dataframe(df.head())
        else:
            st.error("Could not extract post ID from URL")

    st.subheader("Or Upload CSV for Analysis")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file is not None:
        analyze_csv(uploaded_file)
