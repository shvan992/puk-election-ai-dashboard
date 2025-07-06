
import streamlit as st
import pandas as pd
import requests
import re
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup

st.set_page_config(page_title="PUK Election AI Dashboard", layout="wide", page_icon="🌹")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'lang' not in st.session_state:
    st.session_state.lang = 'English'

if not st.session_state.logged_in:
    st.image("puk_logo.png", width=100)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "shvan" and password == "shvan1234":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid credentials")
    st.stop()

st.sidebar.image("puk_logo.png", width=80)
st.sidebar.success("Logged in as: shvan")
st.sidebar.markdown("Prepared by Shvan Qaraman")

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
            html = requests.get(link, headers={"User-Agent": "Mozilla/5.0"}).text
            for pat in [r'"top_level_post_id":"(\d+)"', r'"post_id":"(\d+)"', r'"ft_ent_identifier":"(\d+)"']:
                m = re.search(pat, html)
                if m:
                    return m.group(1)
        return None
    except Exception:
        return None

def fetch_comments(post_id, token):
    url = f"https://graph.facebook.com/v18.0/{post_id}/comments?access_token={token}&limit=100"
    comments = []
    while url:
        res = requests.get(url).json()
        comments += [c.get("message") for c in res.get("data", []) if "message" in c]
        url = res.get("paging", {}).get("next")
    return comments

st.title("📄 PUK Facebook Comment Fetcher")

fb_link = st.text_input("Paste Facebook Post URL")
access_token = st.secrets["FB_ACCESS_TOKEN"] if "FB_ACCESS_TOKEN" in st.secrets else "PASTE_YOUR_ACCESS_TOKEN_HERE"

if st.button("Fetch Comments"):
    pid = extract_post_id(fb_link)
    if pid:
        data = fetch_comments(pid, access_token)
        df = pd.DataFrame(data, columns=["Comment"])
        fname = f"facebook_comments_{pid}.csv"
        df.to_csv(fname, index=False)
        st.success(f"Saved {len(df)} comments to {fname}")
        st.dataframe(df.head())
    else:
        st.error("Could not extract post ID. Please check the link.")
