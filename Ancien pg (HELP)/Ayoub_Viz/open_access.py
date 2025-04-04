import streamlit as st
import pandas as pd
import json
from fuzzywuzzy import fuzz
import plotly.express as px

with open("hal_results.json", "r", encoding="utf-8") as file:
    data = json.load(file)

with open("researchers.txt", "r", encoding="utf-8") as file:
    researchers_list = [line.strip() for line in file]

def find_closest_author(author_name, researchers_list):
    for researcher in researchers_list:
        if fuzz.partial_ratio(author_name.lower(), researcher.lower()) > 80:
            return researcher
    return author_name

records = []
for researcher in data:
    for doc in researcher.get("results", []):
        authors = doc.get("authFullName_s", [])
        primary_domain = doc.get("primaryDomain_s", "Unknown")
        open_access = doc.get("openAccess_bool", False)
        for author in authors:
            matched_author = find_closest_author(author, researchers_list)
            records.append({"Author": matched_author, "Domain": primary_domain, "Open Access": open_access})

df = pd.DataFrame(records)
open_access_stats = df.groupby(["Domain", "Open Access"]).size().reset_index(name="Count")
overall_stats = df["Open Access"].value_counts().reset_index(name="Count")
overall_stats.columns = ["Open Access", "Count"]

st.title("Open Access Publications Analysis")

selected_domain = st.selectbox("Select a Domain", [None] + list(df["Domain"].unique()))

pie_fig = px.pie(
    overall_stats,
    names="Open Access",
    values="Count",
    title="Overall Open Access Proportion",
    color="Open Access",
    color_discrete_map={True: "green", False: "red"}
)
st.plotly_chart(pie_fig)

if selected_domain:
    filtered_stats = open_access_stats[open_access_stats["Domain"] == selected_domain]
else:
    filtered_stats = open_access_stats

bar_fig = px.bar(
    filtered_stats,
    x="Domain",
    y="Count",
    color="Open Access",
    barmode="group",
    title="Open Access by Domain",
    color_discrete_map={True: "green", False: "red"},
    labels={"Open Access": "Open Access (True/False)"}
)
st.plotly_chart(bar_fig)
