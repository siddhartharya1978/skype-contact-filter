import pandas as pd
import streamlit as st
import re

st.set_page_config(page_title="Skype Contact Filter", layout="wide")

st.title("📒 Skype Contact Filter Tool")

# Tags to filter
TAGS = ["+mini", "+hdy", "+smx", "+pmx", "+cape", "+med", "+atl", "+rsea",
        "+safr", "+pg", "+wci", "+eci", "+seas", "+feast", "+nopac", "+aus", "+aust"]

# Upload file
uploaded_file = st.file_uploader("Upload Skype Contacts CSV", type=["csv"])

# Select filter mode
filter_mode = st.radio("Filter Mode", ["AND", "OR"], horizontal=True)

# Select tags
selected_tags = st.multiselect("Tags to Filter", TAGS)

if uploaded_file and selected_tags:
    df = pd.read_csv(uploaded_file)

    if "display_name" not in df.columns:
        st.error("CSV must contain a 'display_name' column.")
    else:
        df["display_name"] = df["display_name"].astype(str).str.lower()

        # Detect country column
        country_col = next((col for col in df.columns if "country" in col.lower()), None)
        if not country_col:
            df["country"] = "N/A"
            country_col = "country"

        if filter_mode == "AND":
            for tag in selected_tags:
                df = df[df["display_name"].str.contains(re.escape(tag))]
        else:
            pattern = "|".join(re.escape(tag) for tag in selected_tags)
            df = df[df["display_name"].str.contains(pattern)]

        st.success(f"Found {len(df)} matching contacts.")
        st.dataframe(df[["display_name", country_col]].rename(columns={country_col: "country"}), use_container_width=True)

        # Optional download
        csv = df.to_csv(index=False)
        st.download_button("📥 Download Filtered CSV", data=csv, file_name="filtered_contacts.csv", mime="text/csv")
