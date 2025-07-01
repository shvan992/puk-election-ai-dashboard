
import streamlit as st
import pandas as pd
import fitz
import matplotlib.pyplot as plt
from textblob import TextBlob
from facebook_scraper import get_posts
from io import BytesIO

st.set_page_config(page_title="PUK AI Dashboard", layout="centered")

def analyze_sentiment(text):
    return TextBlob(text).sentiment.polarity

def label_sentiment(score):
    return "Positive" if score > 0 else "Negative" if score < 0 else "Neutral"

def detect_topic(text):
    topics = {
        "Corruption": ["bribe", "corrupt", "steal", "scandal"],
        "Education": ["school", "education", "university", "student"],
        "Security": ["attack", "police", "security", "violence"],
        "Economy": ["job", "price", "dollar", "salary", "money"],
        "Leadership": ["bafel", "pavel", "talabani", "barzani", "shaswar", "lahur"]
    }
    text = text.lower()
    for topic, keywords in topics.items():
        if any(k in text for k in keywords):
            return topic
    return "Other"

def detect_party(text):
    parties = {
        "PUK": ["puk", "یەکێتی", "talabani", "bafel", "pavel", "mam jalal"],
        "KDP": ["kdp", "پارتی", "barzani", "nechirvan", "masoud"],
        "Gorran": ["گۆڕان", "gorran", "change"],
        "Komal": ["komal", "کۆمەڵ"],
        "Yakgrtu": ["yakgrtu", "yekgrtw", "یەکگرتوو"],
        "New Generation": ["new generation", "نەوەی نوێ", "shaswar"],
        "Barey Gal": ["barey gal", "baray gal", "بەرەی گەل", "lahur", "لەهۆر"]
    }
    text = text.lower()
    for party, keywords in parties.items():
        if any(k in text for k in keywords):
            return party
    return "None"

def show_charts(df):
    st.subheader("📊 Summary Charts")
    col1, col2 = st.columns(2)

    with col1:
        sentiment_counts = df["Sentiment"].value_counts()
        fig1, ax1 = plt.subplots()
        ax1.pie(sentiment_counts, labels=sentiment_counts.index, autopct="%1.1f%%")
        ax1.axis("equal")
        st.markdown("**Sentiment Distribution**")
        st.pyplot(fig1)

    with col2:
        topic_counts = df["Topic"].value_counts().head(5)
        fig2, ax2 = plt.subplots()
        ax2.bar(topic_counts.index, topic_counts.values)
        st.markdown("**Top Topics**")
        st.pyplot(fig2)

def process_comments(comments):
    df = pd.DataFrame(comments, columns=["Comment"])
    df["Sentiment Score"] = df["Comment"].apply(analyze_sentiment)
    df["Sentiment"] = df["Sentiment Score"].apply(label_sentiment)
    df["Topic"] = df["Comment"].apply(detect_topic)
    df["Detected Party"] = df["Comment"].apply(detect_party)
    return df

def fetch_facebook_comments(post_url):
    comments = []
    for post in get_posts(post_urls=[post_url], options={"comments": True}, cookies="cookies.txt"):
        for c in post.get("comments_full", []):
            text = c.get("comment_text", "")
            if text:
                comments.append(text)
        break
    return comments

st.image("puk_logo.png", width=100)
st.title("PUK AI Dashboard")

post_url = st.text_input("🔗 Paste Facebook Post Link:")

if st.button("Fetch and Analyze"):
    if post_url.strip():
        try:
            comments = fetch_facebook_comments(post_url)
            if not comments:
                st.warning("No comments found.")
            else:
                df = process_comments(comments)
                st.dataframe(df)

                # Download buttons
                csv = df.to_csv(index=False).encode("utf-8")
                excel_io = BytesIO()
                df.to_excel(excel_io, index=False, engine="openpyxl")
                excel_io.seek(0)

                st.download_button("⬇️ Download CSV", csv, "facebook_analysis.csv", "text/csv")
                st.download_button("⬇️ Download Excel", excel_io, "facebook_analysis.xlsx", 
                                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                show_charts(df)
        except Exception as e:
            st.error(f"Error fetching Facebook data: {e}")
