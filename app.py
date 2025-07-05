
import streamlit as st
import pandas as pd
import requests
import os
import re
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup

st.set_page_config(page_title="PUK Election AI Dashboard", layout="wide", page_icon="🌹")

def extract_post_id(link):
    try:
        parsed = urlparse(link)
        q = parse_qs(parsed.query)
        if "posts/" in link:
            return link.split("posts/")[1].split("/")[0]
        if "fbid" in q:
            return q["fbid"][0]
        if "story_fbid" in q:
            return q["story_fbid"][0]
        if "/videos/" in link:
            return link.split("/videos/")[1].split("/")[0]
        if "/permalink/" in link:
            return link.split("/permalink/")[1].split("/")[0]
        if "/share/" in link:
            headers = {"User-Agent": "Mozilla/5.0"}
            html = requests.get(link, headers=headers, timeout=10).text
            soup = BeautifulSoup(html, 'html.parser')
            patterns = [
                r'"top_level_post_id":"(\d+)"',
                r'"post_id":"(\d+)"',
                r'"ft_ent_identifier":"(\d+)"'
            ]
            for p in patterns:
                match = re.search(p, html)
                if match:
                    return match.group(1)
        return None
    except Exception:
        return None

def fetch_comments(post_id, token):
    url = f"https://graph.facebook.com/v18.0/{post_id}/comments?access_token={token}&limit=1000"
    comments = []
    while url:
        res = requests.get(url).json()
        comments += [c["message"] for c in res.get("data", []) if "message" in c]
        url = res.get("paging", {}).get("next")
    return comments

st.title("PUK AI Dashboard")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.image("puk_logo.png", width=100)
    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")
    if st.button("Login"):
        if user.strip() == "shvan" and pw == "shvan1234":
            st.session_state.logged_in = True
            st.experimental_rerun()
        else:
            st.error("Invalid credentials")
    st.stop()

st.sidebar.image("puk_logo.png", width=80)
st.sidebar.success("Logged in as: shvan")
st.sidebar.markdown("Prepared by Shvan Qaraman")

st.subheader("Paste Facebook Post Link")
fb_link = st.text_input("Facebook Post URL")
access_token = st.secrets["FB_ACCESS_TOKEN"] if "FB_ACCESS_TOKEN" in st.secrets else "PASTE_YOUR_ACCESS_TOKEN_HERE"

if st.button("Fetch & Convert to CSV"):
    post_id = extract_post_id(fb_link)
    if post_id:
        comments = fetch_comments(post_id, access_token)
        df = pd.DataFrame(comments, columns=["Comment"])
        df.to_csv("facebook_comments.csv", index=False)
        st.success(f"Saved {len(df)} comments to facebook_comments.csv")
        st.dataframe(df.head())
    else:
        st.error("Could not extract post ID from URL — please check the link")

uploaded = st.file_uploader("Upload CSV")
if uploaded:
    df = pd.read_csv(uploaded)
    st.success("CSV uploaded")
    st.dataframe(df.head())
