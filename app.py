import pandas as pd
import streamlit as st
import re
import os
import json

st.set_page_config(page_title="Skype Tool + Charterer Matrix", layout="wide")

CONTACT_FILE = "contacts.csv"
MATRIX_FILE = "channel_matrix.xlsx"
SAVE_FILE = "saved_lists.json"

tabs = st.tabs(["Contact Filter", "Channel Matrix"])

# Load or initialize saved lists
if os.path.exists(SAVE_FILE):
    with open(SAVE_FILE, "r") as f:
        saved_data = json.load(f)
else:
    saved_data = {}

# TAB 1: Contact Filter Tool
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

    ticked_contacts = []

    if selected_tags:
        filtered_df = df.copy()
        if filter_mode == "AND":
            for tag in selected_tags:
                filtered_df = filtered_df[filtered_df["display_name"].str.contains(re.escape(tag))]
        else:
            pattern = "|".join(re.escape(tag) for tag in selected_tags)
            filtered_df = filtered_df[filtered_df["display_name"].str.contains(pattern)]

        st.success(f"Found {len(filtered_df)} matching contacts.")

        with st.expander("✅ Tick off contacts as you check them", expanded=False):
            for i, row in filtered_df.iterrows():
                ticked = st.checkbox(f"**{row['display_name'].title()}**  _( {row['country']} )_", key=f"contact_{i}")
                if ticked:
                    ticked_contacts.append({"display_name": row["display_name"], "country": row["country"]})

        # Save preset block
        if ticked_contacts:
            st.markdown("### 💾 Save this list as a preset")
            preset_name = st.text_input("Enter a name for this contact list")
            if st.button("Save List"):
                if preset_name:
                    saved_data[preset_name] = {
                        "tags": selected_tags,
                        "contacts": ticked_contacts
                    }
                    with open(SAVE_FILE, "w") as f:
                        json.dump(saved_data, f, indent=2)
                    st.success(f"List '{preset_name}' saved successfully!")
                else:
                    st.warning("Please enter a name before saving.")

            # Download button
            csv_data = pd.DataFrame(ticked_contacts).to_csv(index=False)
            st.download_button("📥 Download Ticked Contacts as CSV", data=csv_data, file_name="ticked_contacts.csv", mime="text/csv")
    else:
        st.info("Select at least one tag to filter the contacts.")

    # Load and manage saved lists
    st.markdown("---")
    st.markdown("### 📂 Load or Manage a Saved List")
    if saved_data:
        selected_preset = st.selectbox("Select a saved contact list", list(saved_data.keys()))
        if selected_preset:
            st.markdown(f"**Tags:** `{', '.join(saved_data[selected_preset]['tags'])}`")
            st.markdown("**Contacts in this list:**")
            for c in saved_data[selected_preset]["contacts"]:
                st.markdown(f"- **{c['display_name'].title()}**  _( {c['country']} )_")

            st.markdown("#### 🗑️ Delete or Rename List")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("❌ Delete This List"):
                    del saved_data[selected_preset]
                    with open(SAVE_FILE, "w") as f:
                        json.dump(saved_data, f, indent=2)
                    st.success(f"Deleted list '{selected_preset}'. Please reload the page.")
            with col2:
                new_name = st.text_input("Rename List As", value=selected_preset)
                if st.button("✏️ Rename"):
                    if new_name and new_name != selected_preset:
                        saved_data[new_name] = saved_data.pop(selected_preset)
                        with open(SAVE_FILE, "w") as f:
                            json.dump(saved_data, f, indent=2)
                        st.success(f"Renamed to '{new_name}'. Please reload the page.")
    else:
        st.info("No saved lists available yet.")

# TAB 2: Charterer-Operator Matrix
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
                st.success(f"✅ Operators who work with us for {selected_charterer}'s cargoes (CRH TRADING):")
                for name in yes_ops:
                    st.markdown(f"- **{name}**")
            with col2:
                st.error(f"❌ Operators who won't work with us for {selected_charterer}'s cargoes (CRH TRADING):")
                for name in no_ops:
                    st.markdown(f"- {name}")
    except Exception as e:
        st.warning("Could not load matrix file. Please ensure 'channel_matrix.xlsx' exists.")
        st.text(f"Error: {e}")
