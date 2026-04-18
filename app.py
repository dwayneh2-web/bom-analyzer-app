import streamlit as st
import pandas as pd
from io import BytesIO

st.title("Excel BOM Analyzer")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    st.subheader("Original Data")
    st.dataframe(df)

    # -----------------------------
    # HIGHLIGHT RULES
    # -----------------------------

    non_electronic_keywords = ["SCREW", "WASHER", "NUT", "BOLT", "BRACKET"]

    def highlight_row(row):
        row_text = " ".join(str(x) for x in row.values).upper()

        # Yellow = non-electronic
        if any(word in row_text for word in non_electronic_keywords):
            return ['background-color: yellow'] * len(row)

        # Blue = alternate parts
        if "ALT" in df.columns and pd.notna(row.get("ALT")):
            return ['background-color: lightblue'] * len(row)

        return [''] * len(row)

    st.subheader("Processed Data (Highlighted)")
    st.dataframe(df.style.apply(highlight_row, axis=1))

    # -----------------------------
    # EXPORT TO MULTIPLE SHEETS
    # -----------------------------

    output = BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name="ALL_DATA", index=False)

        if "NHA" in df.columns:
            unique_nhas = df["NHA"].dropna().unique()

            for nha in unique_nhas:
                sheet_name = str(nha)[:31]  # Excel sheet limit
                df[df["NHA"] == nha].to_excel(writer, sheet_name=sheet_name, index=False)

    output.seek(0)

    st.download_button(
        label="Download Processed BOM",
        data=output,
        file_name="processed_bom.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
