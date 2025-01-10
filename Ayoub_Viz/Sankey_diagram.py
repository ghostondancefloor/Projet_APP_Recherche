import dash
from dash import dcc, html, Input, Output
import pandas as pd
import json
import plotly.graph_objects as go

# Load the HAL results JSON file
with open("hal_results.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Prepare data for collaborations
records = []
for researcher in data:
    for doc in researcher.get("results", []):
        authors = doc.get("authFullName_s", [])
        primary_domain = doc.get("primaryDomain_s", "Unknown")
        for author in authors:  # Ensure we extract individual researchers
            records.append({"Researcher": author, "Domain": primary_domain})

# Convert to DataFrame
df = pd.DataFrame(records)

# Aggregate collaborations (count number of publications per researcher-domain pair)
collaborations = df.groupby(["Researcher", "Domain"]).size().reset_index(name="Count")

# Extract unique researchers
researchers = collaborations["Researcher"].unique()

# Dash App
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Sankey Diagram of Researcher Domains", style={"text-align": "center"}),

    # Researcher filter dropdown
    html.Div([
        html.Label("Select a Researcher:"),
        dcc.Dropdown(
            id="researcher-dropdown",
            options=[{"label": res, "value": res} for res in researchers],
            value=None,
            placeholder="Select a researcher"
        ),
    ], style={"width": "50%", "margin": "auto"}),

    # Sankey Diagram
    dcc.Graph(id="sankey-diagram"),

    html.P("Note: The Sankey diagram shows the number of publications a researcher has in each domain.",
           style={"text-align": "center", "font-size": "14px", "color": "gray"})
])


@app.callback(
    Output("sankey-diagram", "figure"),
    Input("researcher-dropdown", "value")
)
def update_sankey(selected_researcher):
    if not selected_researcher:
        # Default graph: Show aggregate data for the top 10 researchers and domains
        top_researchers = collaborations.groupby("Researcher")["Count"].sum().nlargest(10).index
        filtered_collaborations = collaborations[
            collaborations["Researcher"].isin(top_researchers)
        ]

        nodes = list(filtered_collaborations["Researcher"].unique()) + list(filtered_collaborations["Domain"].unique())
        node_mapping = {name: i for i, name in enumerate(nodes)}

        links = {
            "source": [node_mapping[row["Researcher"]] for _, row in filtered_collaborations.iterrows()],
            "target": [node_mapping[row["Domain"]] for _, row in filtered_collaborations.iterrows()],
            "value": filtered_collaborations["Count"].tolist()
        }

        # Create aggregate Sankey diagram
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

        fig.update_layout(title_text="Top 10 Researchers and Their Domains", font_size=10)
        return fig

    # Filter data for the selected researcher
    filtered_collaborations = collaborations[
        collaborations["Researcher"] == selected_researcher
    ]

    # Prepare nodes and links for Sankey diagram
    domains = filtered_collaborations["Domain"].unique()
    nodes = [selected_researcher] + list(domains)
    node_mapping = {name: i for i, name in enumerate(nodes)}

    links = {
        "source": [node_mapping[selected_researcher]] * len(filtered_collaborations),
        "target": [node_mapping[domain] for domain in filtered_collaborations["Domain"]],
        "value": filtered_collaborations["Count"].tolist()
    }

    # Create Sankey diagram
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
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
