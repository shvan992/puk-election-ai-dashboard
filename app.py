
import streamlit as st
import pandas as pd

st.set_page_config(page_title="PUK Election AI Dashboard", layout="wide")
st.title("PUK Election AI Dashboard")

uploaded_file = st.file_uploader("Upload Facebook Comments/Post file (CSV, Excel, PDF)", type=["csv", "xlsx", "xls", "pdf"])
if uploaded_file:
    st.success("File uploaded!")
    st.write("Preview of uploaded file:")
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.DataFrame({"Content": ["(PDF parsing not shown in demo)"]})
    st.dataframe(df.head())

    st.write("Party Mentions:")
    parties = ["یەکێتی", "پارتی", "گۆڕان", "کۆمەڵ", "یەکگرتوو", "بەرەی گەل", "هەلوێست"]
    for party in parties:
        count = df.astype(str).apply(lambda row: row.str.contains(party)).sum().sum()
        st.write(f"{party}: {count} mentions")
