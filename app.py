
import streamlit as st
import pandas as pd
import uuid
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt

st.set_page_config(page_title="PUK AI Dashboard", layout="centered")

# ---- Logo & Header ----
st.image("logo.png", width=130)
st.title("PUK AI Dashboard")
st.markdown("<div style='text-align: right; font-size: 13px; color: gray;'>Prepared by <strong>Shvan Qaraman</strong></div>", unsafe_allow_html=True)

# Language selector (placeholder)
lang = st.selectbox("🌐 Language / زمان", ["English", "کوردی", "عربي"])

# ---- Login ----
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    with st.form("login"):
        st.subheader("Login")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            if u == "shvan" and p == "shvan1234":
                st.session_state.logged_in = True
                st.experimental_rerun()
            else:
                st.error("Invalid credentials!")
    st.stop()

# ---- Helper Functions ----
analyzer = SentimentIntensityAnalyzer()
PARTIES = ["یەکێتی", "پارتی", "گۆڕان", "کۆمەڵ", "یەکگرتوو", "بەرەی گەل", "هەلوێست"]

@st.cache_data(show_spinner=False)
def analyze_dataframe(df):
    # Sentiment
    sentiments = []
    for text in df['Comment'].astype(str):
        score = analyzer.polarity_scores(text)
        compound = score['compound']
        if compound >= 0.05:
            sentiments.append("Positive")
        elif compound <= -0.05:
            sentiments.append("Negative")
        else:
            sentiments.append("Neutral")

    df['Sentiment'] = sentiments

    # Party counts
    party_counts = {p: df['Comment'].astype(str).str.contains(p).sum() for p in PARTIES}
    sentiment_counts = df['Sentiment'].value_counts().to_dict()
    return df, party_counts, sentiment_counts

def render_charts(party_counts, sentiment_counts):
    st.subheader("Party Mentions (0 - 100K+ Comments)")
    if party_counts:
        parties, counts = zip(*party_counts.items())
        chart_data = pd.DataFrame({"Party": parties, "Mentions": counts})
        st.bar_chart(chart_data.set_index("Party"))

    st.subheader("Sentiment Distribution")
    if sentiment_counts:
        labels, values = zip(*sentiment_counts.items())
        chart_data = pd.DataFrame({"Sentiment": labels, "Count": values})
        st.bar_chart(chart_data.set_index("Sentiment"))

# ---- Main Workflow ----
tab1, tab2 = st.tabs(["Paste Facebook Link", "Upload File"])

with tab1:
    fb_link = st.text_input("Paste Facebook post link here")
    if fb_link:
        st.info("Simulating extraction... Works with up to 100,000 comments.")
        # Simulate 5 sample comments; replace with real API integration
        sample_comments = [
            "پارتی دەبێت لەسەر هەڵوێستی خۆی بیستووری بکات",
            "من پشتیوانی یەکێتی دەکەم",
            "بەرەی گەل و هەلوێست دەبن جلوبەرگی نوێ",
            "گۆڕان هەستی نوێیان پێشکەش کردووە",
            "یەکگرتوو گرنگە لە هەرێم"
        ]
        df = pd.DataFrame({"Comment": sample_comments})
        analyzed_df, party_counts, sentiment_counts = analyze_dataframe(df)
        st.success("Analysis complete!")
        st.dataframe(analyzed_df.head())

        render_charts(party_counts, sentiment_counts)

        # Offer CSV download
        csv_name = f"{uuid.uuid4().hex[:6]}_comments_analysis.csv"
        analyzed_df.to_csv(csv_name, index=False)
        st.download_button("Download CSV", data=analyzed_df.to_csv(index=False), file_name=csv_name, mime="text/csv")

with tab2:
    up_file = st.file_uploader("Upload CSV or Excel (up to 100,000 comments)", type=["csv", "xlsx", "xls"])
    if up_file:
        if up_file.name.endswith(".csv"):
            df = pd.read_csv(up_file, low_memory=False)
        else:
            df = pd.read_excel(up_file)
        if 'Comment' not in df.columns:
            df.columns = ['Comment'] + list(df.columns[1:])

        st.info(f"Loaded {len(df):,} comments.")
        analyzed_df, party_counts, sentiment_counts = analyze_dataframe(df)
        st.success("Analysis complete!")
        st.dataframe(analyzed_df.head())

        render_charts(party_counts, sentiment_counts)

        csv_name = f"{uuid.uuid4().hex[:6]}_comments_analysis.csv"
        st.download_button("Download CSV", data=analyzed_df.to_csv(index=False), file_name=csv_name, mime="text/csv")
