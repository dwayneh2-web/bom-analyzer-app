import streamlit as st
import pandas as pd

st.title("Excel Analyzer App")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    st.subheader("Raw Data")
    st.write(df)

    st.subheader("Column Names")
    st.write(df.columns)

    st.subheader("Summary Stats")
    st.write(df.describe())

    st.subheader("Rows with Missing Data")
    missing = df[df.isnull().any(axis=1)]
    st.write(missing)

    if "Amount" in df.columns:
        st.subheader("High Values (Above Average)")
        high = df[df["Amount"] > df["Amount"].mean()]
        st.write(high)s