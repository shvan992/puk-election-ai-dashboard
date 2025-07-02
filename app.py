
import streamlit as st
import pandas as pd
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

st.set_page_config(page_title="PUK AI Dashboard", layout="centered")

# Header
st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Patriotic_Union_of_Kurdistan_emblem.svg/1024px-Patriotic_Union_of_Kurdistan_emblem.svg.png", width=120)
st.title("PUK AI Dashboard")
st.markdown("<div style='text-align:right;color:gray;'>Prepared by <strong>Shvan Qaraman</strong></div>", unsafe_allow_html=True)

analyzer = SentimentIntensityAnalyzer()
PARTIES = ["یەکێتی","پارتی","گۆڕان","کۆمەڵ","یەکگرتوو","بەرەی گەل","هەلوێست"]

# 1. Convert Facebook link to CSV (simulation)
st.subheader("Step 1 – Convert Facebook link ➜ CSV")
link = st.text_input("Paste public Facebook post link")
if st.button("Fetch & Save CSV"):
    if link.strip() == "":
        st.error("Please paste a link.")
    else:
        comments = [
            "یەکێتی بەرنامەی باشی هەیە",
            "پارتی گرنگە لەسەر هۆکاری ئابوری",
            "گۆڕان کەس نەزانێت چی دەکات",
            "کۆمەڵ پشتیوانی زۆری هەیە",
            "بەرەی گەل دەبێت پوختەیەکی نوێ پێشکەش بکات"
        ]
        df = pd.DataFrame({"Comment": comments})
        csv = df.to_csv(index=False).encode()
        st.download_button("Download CSV", data=csv, file_name="facebook_comments.csv", mime="text/csv")
        st.success("CSV ready – download above, then go to Step 2.")

# 2. Upload CSV and analyze
st.subheader("Step 2 – Upload CSV and Analyze")
up_file = st.file_uploader("Upload CSV file", type=["csv"])
if up_file and st.button("Analyze CSV"):
    df = pd.read_csv(up_file)
    df["Sentiment"] = df["Comment"].apply(
        lambda c: "Positive" if analyzer.polarity_scores(str(c))["compound"] >= 0.05 else ("Negative" if analyzer.polarity_scores(str(c))["compound"] <= -0.05 else "Neutral")
    )
    counts = {p: df["Comment"].str.contains(p).sum() for p in PARTIES}
    st.dataframe(df.head())
    st.bar_chart(pd.DataFrame.from_dict(counts, orient="index", columns=["Mentions"]))
    st.bar_chart(df["Sentiment"].value_counts())
    st.download_button("Download analyzed CSV", data=df.to_csv(index=False), file_name="analyzed_comments.csv", mime="text/csv")
