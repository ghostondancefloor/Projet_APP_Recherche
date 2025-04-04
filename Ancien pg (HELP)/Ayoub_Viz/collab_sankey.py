import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
from datetime import datetime, timedelta
from fuzzywuzzy import fuzz

# Load the HAL results JSON file
with open("hal_results.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Load the researchers list for reference
with open("researchers.txt", "r", encoding="utf-8") as file:
    researchers_list = [line.strip() for line in file]

# Function to find the closest author match
def find_closest_author(author_name, researchers_list):
    for researcher in researchers_list:
        if fuzz.partial_ratio(author_name.lower(), researcher.lower()) > 80:
            return researcher
    return None

# Prepare data for collaboration analysis
records = []
for researcher in data:
    for doc in researcher.get("results", []):
        authors = doc.get("authFullName_s", [])
        publication_date = doc.get("publicationDate_s", "Unknown")
        if publication_date != "Unknown":
            try:
                date_obj = datetime.strptime(publication_date, "%Y-%m-%d")
                for author in authors:
                    matched_author = find_closest_author(author, researchers_list)
                    if matched_author:
                        for coauthor in authors:
                            if author != coauthor:
                                matched_coauthor = find_closest_author(coauthor, researchers_list)
                                if matched_coauthor:
                                    records.append({
                                        "Source": matched_author,
                                        "Target": matched_coauthor,
                                        "Date": date_obj
                                    })
            except ValueError:
                continue

# Convert to DataFrame
df = pd.DataFrame(records)

# Streamlit App
st.title("Collaboration Sankey Diagram (LISTIC Only)")

# Filters
selected_researcher = st.selectbox("Select a Researcher", sorted(df["Source"].unique()), index=0)
time_range = st.radio("Select Time Range", [1, 2, 5, 10], format_func=lambda x: f"Last {x} Years")

# Filter data
cutoff_date = datetime.now() - timedelta(days=365 * time_range)
filtered_data = df[(df["Date"] >= cutoff_date) & (df["Source"] == selected_researcher)]

if filtered_data.empty:
    st.write("No collaborations found for the selected criteria.")
else:
    sankey_data = filtered_data.groupby(["Source", "Target"]).size().reset_index(name="Count")
    nodes = list(set(sankey_data["Source"]).union(set(sankey_data["Target"])))
    node_mapping = {name: i for i, name in enumerate(nodes)}

    links = {
        "source": [node_mapping[row["Source"]] for _, row in sankey_data.iterrows()],
        "target": [node_mapping[row["Target"]] for _, row in sankey_data.iterrows()],
        "value": sankey_data["Count"].tolist()
    }

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=nodes,
        ),
        link=dict(
            source=links["source"],
            target=links["target"],
            value=links["value"]
        )
    )])

    fig.update_layout(title_text=f"Collaboration Sankey Diagram for {selected_researcher} (Last {time_range} Years)", font_size=10)
    st.plotly_chart(fig)
