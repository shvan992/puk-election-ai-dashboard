
import streamlit as st
import pandas as pd
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt

st.set_page_config(page_title="PUK Election AI Dashboard", layout="centered")
st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Patriotic_Union_of_Kurdistan_emblem.svg/1200px-Patriotic_Union_of_Kurdistan_emblem.svg.png", width=130)
st.title("PUK AI Dashboard")
st.markdown("<div style='text-align: right; font-size: 13px; color: gray;'>Prepared by <strong>Shvan Qaraman</strong></div>", unsafe_allow_html=True)

analyzer = SentimentIntensityAnalyzer()
PARTIES = ["یەکێتی", "پارتی", "گۆڕان", "کۆمەڵ", "یەکگرتوو", "بەرەی گەل", "هەلوێست"]

def get_post_id_from_share_link(link):
    import re
    try:
        response = requests.get(link, allow_redirects=True)
        final_url = response.url
        match = re.search(r"/posts/(\d+)", final_url)
        if match:
            return match.group(1)
        return final_url.split("/")[-1].split("?")[0]
    except:
        return None

def fetch_comments(post_id, limit=500):
    all_comments = []
    url = f"https://graph.facebook.com/v19.0/{post_id}/comments?access_token=" + ACCESS_TOKEN + "&limit=100"
    while url and len(all_comments) < limit:
        r = requests.get(url)
        if r.status_code != 200:
            st.error("Error fetching comments from Facebook.")
            return []
        data = r.json()
        comments = [c['message'] for c in data.get('data', []) if 'message' in c]
        all_comments.extend(comments)
        paging = data.get('paging', {})
        url = paging.get('next')
    return all_comments[:limit]

def analyze_comments(comments):
    results = []
    for c in comments:
        score = analyzer.polarity_scores(c)['compound']
        sentiment = "Neutral"
        if score >= 0.05:
            sentiment = "Positive"
        elif score <= -0.05:
            sentiment = "Negative"
        results.append({"Comment": c, "Sentiment": sentiment})
    return pd.DataFrame(results)

def count_parties(df):
    party_counts = {party: df['Comment'].str.contains(party).sum() for party in PARTIES}
    return party_counts

ACCESS_TOKEN = "EAAQuTsUxpHYBO3VTnECXDzoEZBtgcKxgZBzlJOrgxk0FRawjo4FlE5qPgJZAgg8IYWvcdPduwBEYZCHEIZCs0E1QecYG6bW6yh4N4tUZCS99dVd8k1AnBXlTMPvOw4h0n4nh1HO3d5KYmeZAkqbozvirjRkTZAXJAKbA8woXpJZA6tkplKVf9WUMbMEIzDQajZBptIZBUAiM8GFzwYuCA7yosIYnGrsjJhPEPrzVraT6OfKBo5Bl9jZBYJlBIX53jVDHFFia5OZCyVGT8R1ZBS"

link = st.text_input("Paste Facebook post link")
if link:
    with st.spinner("Fetching and analyzing..."):
        post_id = get_post_id_from_share_link(link)
        if not post_id:
            st.error("Could not extract post ID.")
        else:
            comments = fetch_comments(post_id)
            if comments:
                df = analyze_comments(comments)
                party_counts = count_parties(df)
                st.success(f"Fetched {len(df)} comments.")
                st.dataframe(df.head())

                st.subheader("Party Mentions")
                st.bar_chart(pd.DataFrame.from_dict(party_counts, orient='index', columns=['Mentions']))

                st.subheader("Sentiment Distribution")
                st.bar_chart(df['Sentiment'].value_counts())

                st.download_button("Download CSV", data=df.to_csv(index=False), file_name="comments_analysis.csv", mime="text/csv")
