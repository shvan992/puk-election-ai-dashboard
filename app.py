
import streamlit as st
import pandas as pd
import requests
import os
from urllib.parse import urlparse, parse_qs

st.set_page_config(page_title="PUK Election AI Dashboard", layout="wide")

st.markdown("""
    <style>
    .main {background-color: #f4f4f4;}
    .stApp {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 2rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    .header-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f5b4c;
    }
    .footer {
        position: fixed;
        bottom: 10px;
        right: 20px;
        font-size: 0.9rem;
        color: #888;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='header-title'>PUK AI Dashboard</div>", unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.image("puk_logo.png", width=100)
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    lang = st.selectbox("Language", ["English", "Kurdish", "Arabic"])
    if st.button("Login"):
        if username.strip() == "shvan" and password == "shvan1234":
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
    try:
        parsed = urlparse(link)
        if "posts/" in link:
            return link.split("posts/")[1].split("/")[0]
        elif "photo" in link and "fbid=" in link:
            return parse_qs(parsed.query).get("fbid", [None])[0]
        elif "story_fbid" in link:
            return parse_qs(parsed.query).get("story_fbid", [None])[0]
        elif "/videos/" in link:
            return link.split("/videos/")[1].split("/")[0]
        elif "/permalink/" in link:
            return link.split("/permalink/")[1].split("/")[0]
        elif "/share/" in link:
            # Try fallback fetch (as last resort — not always reliable)
            response = requests.get(link, headers={"User-Agent": "Mozilla/5.0"})
            match = re.search(r'"top_level_post_id":"(\d+)"', response.text)
            if match:
                return match.group(1)
        return None
    except Exception:
        return None

if not st.session_state.logged_in:
    login()
else:
    st.sidebar.image("puk_logo.png", width=80)
    st.sidebar.success("Logged in as: shvan")
    st.sidebar.markdown("<div class='footer'>Prepared by Shvan Qaraman</div>", unsafe_allow_html=True)

    st.subheader("Paste Facebook Post Link")
    fb_link = st.text_input("Facebook Post URL")
    access_token = st.secrets["FB_ACCESS_TOKEN"] if "FB_ACCESS_TOKEN" in st.secrets else "PASTE_YOUR_ACCESS_TOKEN_HERE"

    if st.button("Fetch & Convert to CSV"):
        post_id = extract_post_id(fb_link)
        if post_id:
            comments = fetch_comments_from_facebook(post_id, access_token)
            df = pd.DataFrame(comments, columns=["Comment"])
            df.to_csv("facebook_comments.csv", index=False)
            st.success("Comments saved to facebook_comments.csv")
            st.dataframe(df.head())
        else:
            st.error("Could not extract post ID from URL — please check the link")

    st.subheader("Or Upload CSV for Analysis")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file is not None:
        analyze_csv(uploaded_file)
