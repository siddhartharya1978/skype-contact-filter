import pandas as pd
import streamlit as st
import re

st.set_page_config(page_title="Skype Contact Filter", layout="wide")
st.title("📒 Skype Contact Filter Tool")

# Define the path to the built-in contact CSV
CONTACT_FILE = "contacts.csv"

# Tags to filter
TAGS = ["+mini", "+hdy", "+smx", "+pmx", "+cape", "+med", "+atl", "+rsea",
        "+safr", "+pg", "+wci", "+eci", "+seas", "+feast", "+nopac", "+aus", "+aust"]

# Load contacts
df = pd.read_csv(CONTACT_FILE)
df["display_name"] = df["display_name"].astype(str).str.lower()

# Ensure 'country' column exists
if "country" not in df.columns:
    df["country"] = "N/A"

# Filter mode
filter_mode = st.radio("Filter Mode", ["AND", "OR"], horizontal=True)

# Tag checkboxes
st.markdown("### Select Tags to Filter")
selected_tags = []
cols = st.columns(6)
for i, tag in enumerate(TAGS):
    if cols[i % 6].checkbox(tag):
        selected_tags.append(tag)

# Filter contacts
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
