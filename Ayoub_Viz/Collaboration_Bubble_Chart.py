import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import json

# Load the HAL results JSON file
with open("hal_results.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Extract collaboration data
collaboration_counts = {}
collaborations = []
domains = {}
for researcher in data:
    for doc in researcher.get("results", []):
        authors = doc.get("authFullName_s", [])
        domain = doc.get("primaryDomain_s", "Unknown")
        for author in authors:
            if author not in collaboration_counts:
                collaboration_counts[author] = 0
                domains[author] = domain
            collaboration_counts[author] += len(authors) - 1  # Count collaborations (excluding self)
            for coauthor in authors:
                if author != coauthor:
                    collaborations.append({"Source": author, "Target": coauthor})

# Convert to DataFrame
df = pd.DataFrame({
    "Researcher": list(collaboration_counts.keys()),
    "Collaboration Count": list(collaboration_counts.values()),
    "Domain": [domains[author] for author in collaboration_counts.keys()]
})

# Convert collaborations to DataFrame for filtering
collab_df = pd.DataFrame(collaborations)

# Dash App
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Collaboration Bubble Chart"),
    dcc.Dropdown(
        id="researcher-filter",
        options=[{"label": name, "value": name} for name in sorted(df["Researcher"])],
        placeholder="Select a Researcher",
        style={"width": "50%", "margin": "auto"}
    ),
    dcc.Graph(id="bubble-chart")
])

@app.callback(
    Output("bubble-chart", "figure"),
    Input("researcher-filter", "value")
)
def update_chart(selected_researcher):
    if selected_researcher:
        # Filter for collaborations involving the selected researcher
        filtered_collab = collab_df[collab_df["Source"] == selected_researcher]
        coauthors = filtered_collab["Target"].tolist()

        # Create a filtered dataset
        filtered_df = df[df["Researcher"].isin([selected_researcher] + coauthors)]

        # Highlight the selected researcher
        filtered_df["IsSelected"] = filtered_df["Researcher"].apply(lambda x: x == selected_researcher)

        # Create bubble chart
        fig = px.scatter(
            filtered_df,
            x="Researcher",
            y="Collaboration Count",
            size="Collaboration Count",
            color="Domain",
            hover_name="Researcher",
            size_max=50,
            title=f"Collaboration Bubble Chart for {selected_researcher}"
        )

        # Adjust marker style for highlighting
        fig.update_traces(marker=dict(
            line=dict(width=2, color="black"),
            opacity=filtered_df["IsSelected"].apply(lambda x: 1.0 if x else 0.6)
        ))

        return fig

    # Default view (no researcher selected)
    fig = px.scatter(
        df,
        x="Researcher",
        y="Collaboration Count",
        size="Collaboration Count",
        color="Domain",
        hover_name="Researcher",
        size_max=50,
        title="Collaboration Bubble Chart"
    )
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)
