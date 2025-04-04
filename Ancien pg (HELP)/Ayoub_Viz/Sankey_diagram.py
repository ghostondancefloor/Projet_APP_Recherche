import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
from fuzzywuzzy import fuzz

# Load the data
with open("hal_results.json", "r", encoding="utf-8") as file:
    data = json.load(file)

with open("researchers.txt", "r", encoding="utf-8") as file:
    researchers_list = [line.strip() for line in file]

def find_closest_author(author_name, researchers_list):
    for researcher in researchers_list:
        if fuzz.partial_ratio(author_name.lower(), researcher.lower()) > 80:
            return researcher
    return None

records = []
for researcher in data:
    for doc in researcher.get("results", []):
        authors = doc.get("authFullName_s", [])
        primary_domain = doc.get("primaryDomain_s", "Unknown")
        for author in authors:
            matched_author = find_closest_author(author, researchers_list)
            if matched_author:
                records.append({"Researcher": matched_author, "Domain": primary_domain})

df = pd.DataFrame(records)
collaborations = df.groupby(["Researcher", "Domain"]).size().reset_index(name="Count")
researchers = collaborations["Researcher"].unique()

st.title("Sankey Diagram of Researcher Domains (LISTIC Only)")

selected_researcher = st.selectbox("Select a Researcher", sorted(researchers), index=0)

filtered_collaborations = collaborations[collaborations["Researcher"] == selected_researcher]
if filtered_collaborations.empty:
    st.write("No data found for the selected researcher.")
else:
    domains = filtered_collaborations["Domain"].unique()
    nodes = [selected_researcher] + list(domains)
    node_mapping = {name: i for i, name in enumerate(nodes)}

    links = {
        "source": [node_mapping[selected_researcher]] * len(filtered_collaborations),
        "target": [node_mapping[domain] for domain in filtered_collaborations["Domain"]],
        "value": filtered_collaborations["Count"].tolist()
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

    fig.update_layout(title_text=f"Domains of Interest for {selected_researcher}", font_size=10)
    st.plotly_chart(fig)
