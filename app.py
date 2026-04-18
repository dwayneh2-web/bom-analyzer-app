import streamlit as st
import pandas as pd
from io import BytesIO

st.title("Excel BOM Analyzer (ACCURIS Formatter)")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    st.subheader("Original Data")
    st.dataframe(df)

    # -----------------------------
    # STANDARD COLUMN MAPPING
    # -----------------------------
    column_mapping = {
        "OEM Item #": "Internal P/N/OEM Part #",
        "BOM Part #": "Internal P/N/OEM Part #",
        "Revision Designator": "OEM Rev.",
        "OEM Cage Code": "OEM CAGE",
        "Manufacturer Part #": "OCM Part #",
        "Alternate Part #": "Alternate Part #",
        "Manufacturer Cage Code": "OCM CAGE",
        "Part Description": "PART DESCRIPTION",
        "Quantity": "UPA/QTY",
        "Reference Designator": "Ref. Designator",
        "NHA Item Number": "NHA",
        "FIIN": "FIIN"
    }

    df = df.rename(columns=column_mapping)

    # Ensure required columns exist
    required_columns = [
        "Internal P/N/OEM Part #",
        "OEM Rev.",
        "OEM CAGE",
        "OCM Part #",
        "Alternate Part #",
        "OCM CAGE",
        "PART DESCRIPTION",
        "UPA/QTY",
        "Ref. Designator",
        "NHA",
        "FIIN"
    ]

    for col in required_columns:
        if col not in df.columns:
            df[col] = ""

    df = df[required_columns]

    # -----------------------------
    # FILTERING LOGIC
    # -----------------------------
    non_electronic_keywords = ["SCREW", "WASHER", "NUT", "BOLT", "BRACKET"]

    def is_non_electronic(row):
        text = str(row["PART DESCRIPTION"]).upper()
        return any(word in text for word in non_electronic_keywords)

    def is_zero_qty(row):
        val = str(row["UPA/QTY"]).strip()
        return val.startswith("0")

    # Split data
    non_electronic_df = df[
        df.apply(is_non_electronic, axis=1) |
        df.apply(is_zero_qty, axis=1)
    ]

    clean_df = df.drop(non_electronic_df.index)

    # -----------------------------
    # DISPLAY RESULTS
    # -----------------------------
    st.subheader("Clean BOM (Ready for ACCURIS)")
    st.dataframe(clean_df)

    st.subheader("Removed Components (Non-Electronic / Zero Qty)")
    st.dataframe(non_electronic_df)

    # -----------------------------
    # EXPORT
    # -----------------------------
    output = BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        clean_df.to_excel(writer, sheet_name="CLEAN_BOM", index=False)
        non_electronic_df.to_excel(writer, sheet_name="NON_ELECTRONIC", index=False)

    output.seek(0)

    st.download_button(
        label="Download Processed BOM",
        data=output,
        file_name="processed_bom.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
