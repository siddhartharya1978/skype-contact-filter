import pandas as pd
import streamlit as st
import re

st.set_page_config(page_title="Skype Tool + Charterer Matrix", layout="wide")

# Define file paths
CONTACT_FILE = "contacts.csv"
MATRIX_FILE = "channel_matrix.xlsx"

# ---------- TABS ----------
tabs = st.tabs(["Contact Filter", "Channel Matrix"])

# ---------- TAB 1: Contact Filter Tool ----------
with tabs[0]:
    st.title("📒 Skype Contact Filter Tool")

    TAGS = ["+mini", "+hdy", "+smx", "+pmx", "+cape", "+med", "+atl", "+rsea",
            "+safr", "+pg", "+wci", "+eci", "+seas", "+feast", "+nopac", "+aus", "+aust"]

    df = pd.read_csv(CONTACT_FILE)
    df["display_name"] = df["display_name"].astype(str).str.lower()
    if "country" not in df.columns:
        df["country"] = "N/A"

    filter_mode = st.radio("Filter Mode", ["AND", "OR"], horizontal=True)

    st.markdown("### Select Tags to Filter")
    selected_tags = []
    cols = st.columns(6)
    for i, tag in enumerate(TAGS):
        if cols[i % 6].checkbox(tag):
            selected_tags.append(tag)

    if selected_tags:
        filtered_df = df.copy()
        if filter_mode == "AND":
            for tag in selected_tags:
                filtered_df = filtered_df[filtered_df["display_name"].str.contains(re.escape(tag))]
        else:
            pattern = "|".join(re.escape(tag) for tag in selected_tags)
            filtered_df = filtered_df[filtered_df["display_name"].str.contains(pattern)]

        st.success(f"Found {len(filtered_df)} matching contacts.")
        st.markdown("### ✅ Tick off contacts as you check them:")
        for i, row in filtered_df.iterrows():
            st.checkbox(f"**{row['display_name'].title()}**  _( {row['country']} )_", key=f"contact_{i}")
    else:
        st.info("Select at least one tag to filter the contacts.")

# ---------- TAB 2: Charterer-Operator Matrix ----------
with tabs[1]:
    st.title("📊 Channel Matrix Checker")

    try:
        matrix_df = pd.read_excel(MATRIX_FILE)
        matrix_df = matrix_df.rename(columns={matrix_df.columns[0]: "Operator"})

        charterers = list(matrix_df.columns[1:])
        selected_charterer = st.selectbox("Select a Charterer", charterers)

        if selected_charterer:
            yes_ops = matrix_df[matrix_df[selected_charterer].astype(str).str.upper() == "YES"]["Operator"]
            no_ops = matrix_df[matrix_df[selected_charterer].astype(str).str.upper() == "NO"]["Operator"]

            col1, col2 = st.columns(2)
            with col1:
                st.success(f"✅ Operators who work {selected_charterer}'s cargoes:")
                for name in yes_ops:
                    st.markdown(f"- **{name}**")
            with col2:
                st.error(f"❌ Operators who DO NOT work {selected_charterer}'s cargoes:")
                for name in no_ops:
                    st.markdown(f"- {name}")
    except Exception as e:
        st.warning("Could not load matrix file. Please ensure 'channel_matrix.xlsx' exists.")
        st.text(f"Error: {e}")
