import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import random
import networkx as nx

with open("aggregated_data.json", "r", encoding="utf-8") as file:
    data = json.load(file)

rows = []
for entry in data:
    year = entry.get("year")  
    for country_data in entry.get("countries", []):
        if country_data.get("country") == "France":
            rows.append({"year": year, "country": country_data.get("country"), "count": 0})
        else:
            rows.append({"year": year, "country": country_data.get("country"), "count": country_data.get("count")})

df = pd.DataFrame(rows)

df1 = pd.read_csv('assets/hal_results.csv')
df2 = pd.read_csv('assets/hal_results.csv')
with open('assets/hal_results_cleaned.json', 'r', encoding='utf-8') as file:
    university_data = json.load(file)
with open("assets/sankey_data.json", "r", encoding="utf-8") as f:
    sankey_data = json.load(f)
with open('assets/graph_edges.json', 'r', encoding='utf-8') as f:
    graph_data = json.load(f)

def preprocess_dates(date_str):
    if pd.isna(date_str):
        return None
    if len(date_str) == 4:  
        return f"{date_str}-01-01"
    elif len(date_str) == 7:  
        return f"{date_str}-01"
    return date_str

for df_tmp in [df1, df2]:
    df_tmp['publicationDate_s'] = df_tmp['publicationDate_s'].apply(preprocess_dates)
    df_tmp['publicationDate_s'] = pd.to_datetime(df_tmp['publicationDate_s'], errors='coerce')
    df_tmp['publicationYear'] = df_tmp['publicationDate_s'].dt.year
    df_tmp['publicationMonth'] = df_tmp['publicationDate_s'].dt.to_period('M')

def analyze_data(data, professor_name, start_year, end_year):
    universities = []
    for entry in data:
        if entry["name"].lower() == professor_name.lower():
            for result in entry.get("results", []):
                publication_year = result.get("publicationDate_s", "").split("-")[0]
                if publication_year.isdigit() and start_year <= int(publication_year) <= end_year:
                    universities.extend(result.get("instStructName_s", []))
    return Counter(universities).most_common(10)

def generate_colors(labels):
    random.seed(42)
    return {label: f"rgba({random.randint(0,255)}, {random.randint(0,255)}, {random.randint(0,255)}, 0.8)" for label in labels}

def generate_sankey(chercheur_name):
    sources, targets, values, labels = [], [], [], []
    label_map, current_index = {}, 0

    for entry in sankey_data:
        if entry["source"] == chercheur_name:
            source, target, value = entry["source"], entry["target"], entry["value"]

            if source not in label_map:
                label_map[source] = current_index
                labels.append(source)
                current_index += 1

            if target not in label_map:
                label_map[target] = current_index
                labels.append(target)
                current_index += 1

            sources.append(label_map[source])
            targets.append(label_map[target])
            values.append(value)

    color_map = generate_colors(labels)

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color=[color_map[label] for label in labels],
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=[color_map[labels[t]] for t in targets],
        )
    )])

    fig.update_layout(
        title_text=f"Diagramme de Sankey pour {chercheur_name}",
        font=dict(size=12, color="black", family="Arial"),
        height=700, width=1000,
        margin=dict(l=0, r=0, t=40, b=40)
    )
    return fig

st.set_page_config(layout="wide")  
st.sidebar.title("Filtres")
years = sorted(df["year"].unique())
selected_year = st.sidebar.slider("Sélectionnez une année", min_value=int(min(years)), max_value=int(max(years)), value=int(min(years)), step=1)
start_year, end_year = st.sidebar.slider(
    "Période de publication",
    min_value=int(df1['publicationYear'].min()),
    max_value=int(df1['publicationYear'].max()),
    value=(2005, 2010),
    step=1
)

dashboard_df = pd.read_csv("data.csv")

top_articles_per_researcher = dashboard_df.groupby(['researcher', 'title'])['value of cited by'].sum().reset_index()

top_articles_per_researcher = top_articles_per_researcher.sort_values(by=['researcher', 'value of cited by'], ascending=[True, False])

top_5_articles = top_articles_per_researcher.groupby('researcher').head(5)

total_citations_per_researcher = dashboard_df.groupby('researcher')['value of cited by'].sum().reset_index()

total_citations_per_researcher = total_citations_per_researcher.sort_values(by='value of cited by', ascending=False)

top_3_researchers = total_citations_per_researcher.head(3)

selected_dashboard_researcher = st.sidebar.selectbox(
    'Sélectionnez un chercheur pour le dashboard supplémentaire',
    list(top_5_articles['researcher'].unique())
)

filtered_dashboard_data = top_5_articles[top_5_articles['researcher'] == selected_dashboard_researcher]

#-------------------------------------------------------

st.title("Analyse des publications scientifiques")
st.title("        ")

#-------------------------------------------------------

# Visualisation 1 
filtered_df = df[df["year"] == str(selected_year)]
fig_map = px.choropleth(
    filtered_df,
    locations="country",
    locationmode="country names",
    color="count",
    hover_name="country",
    title=f"Carte des pays collaborateurs en {selected_year}",
    color_continuous_scale="Plasma",
    labels={"count": "Nombre", "country": "Pays"}
)
fig_map.add_scattergeo(
    locations=["France"],
    locationmode="country names",
    marker=dict(color="black", size=15),
    name="France (Noire)"
)
fig_map.update_layout(
    height=700,  
    width=1200,  
    margin={"r": 0, "t": 50, "l": 0, "b": 0}  
)
st.plotly_chart(fig_map, use_container_width=True)

col1, col2 = st.columns(2)

# Visualisation 2 
with col1:
    top_5 = filtered_df.sort_values(by="count", ascending=False).head(5)
    fig_bar = px.bar(
        top_5,
        x="country",
        y="count",
        text="count",
        title=f"Top 5 des pays collaborateurs {selected_year}",
        labels={"count": "Nombre", "country": "Pays"}
    )
    fig_bar.update_traces(textposition="outside")
    st.plotly_chart(fig_bar, use_container_width=True)

# Visualisation 3 
with col2:
    filtered_df1 = df1[(df1['publicationYear'] >= start_year) & (df1['publicationYear'] <= end_year)]
    if selected_dashboard_researcher != 'All Researchers':
        filtered_df1 = filtered_df1[filtered_df1['customAuthorName'] == selected_dashboard_researcher]
    publication_count_by_year = filtered_df1.groupby('publicationYear').size().reset_index(name='count')
    fig_pub = px.bar(
        publication_count_by_year,
        x='publicationYear',
        y='count',
        title=f"Publications de {selected_dashboard_researcher}" if selected_dashboard_researcher != 'All Researchers' else "Publications par année",
        labels={'publicationYear': 'Année', 'count': 'Nombre de publications'}
    )
    st.plotly_chart(fig_pub, use_container_width=True)

#-------------------------------------------------------



fig_sankey = generate_sankey(selected_dashboard_researcher)
st.plotly_chart(fig_sankey, use_container_width=True)

col1, col2 = st.columns(2)

# Visualisation 4 
with col1:
    university_counts = analyze_data(university_data, selected_dashboard_researcher, start_year, end_year)
    if university_counts:
        df_chart = {
            "University": [item[0] for item in university_counts],
            "Count": [item[1] for item in university_counts],
        }
        fig_pie = px.pie(df_chart, names="University", values="Count", title=f"Top 10 Universités pour {selected_dashboard_researcher}")
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.warning(f"Aucune publication trouvée pour {selected_dashboard_researcher} entre {start_year} et {end_year}.")

# Visualisation 6 
with col2:
    G = nx.Graph()

    for edge in graph_data:
        source = edge["source"]
        target = edge["target"]
        weight = edge["weight"]
        G.add_edge(source, target, weight=weight)

    pos = nx.spring_layout(G, seed=42)
    x_nodes = [pos[node][0] for node in G.nodes()]
    y_nodes = [pos[node][1] for node in G.nodes()]

    x_edges = []
    y_edges = []
    for edge in G.edges():
        x_edges += [pos[edge[0]][0], pos[edge[1]][0], None]
        y_edges += [pos[edge[0]][1], pos[edge[1]][1], None]

    edge_trace = go.Scatter(
        x=x_edges,
        y=y_edges,
        line=dict(width=0.5, color="gray"),
        hoverinfo="none",
        mode="lines"
    )

    node_trace = go.Scatter(
        x=x_nodes,
        y=y_nodes,
        mode="markers",
        hoverinfo="text",
        marker=dict(
            showscale=True,
            colorscale="YlGnBu",
            size=10,
            colorbar=dict(
                thickness=15,
                title="Node Connections",
                xanchor="left",
                titleside="right"
            )
        )
    )

    node_text = [f"{node}" for node in G.nodes()]
    node_trace.marker.color = [len(list(G.neighbors(node))) for node in G.nodes()]
    node_trace.text = node_text

    fig_graph = go.Figure(data=[edge_trace, node_trace],
                          layout=go.Layout(
                              showlegend=False,
                              hovermode="closest",
                              title="Collaborations entre Chercheurs",
                              xaxis=dict(showgrid=False, zeroline=False),
                              yaxis=dict(showgrid=False, zeroline=False)
                          ))
    st.plotly_chart(fig_graph, use_container_width=True)

#--------------------------------

col1, col2 = st.columns(2)

# Visualisation 7 
with col1:
    collab_count = {}

    for entry in sankey_data:
        source = entry["source"]
        target = entry["target"]
        if source not in collab_count:
            collab_count[source] = set()
        collab_count[source].add(target)

    collab_data = [{"professor": prof, "num_institutes": len(instituts)} for prof, instituts in collab_count.items()]
    collab_df = pd.DataFrame(collab_data)

    fig_collab = px.bar(collab_df, x="professor", y="num_institutes",
                        labels={"professor": "Nom du Professeur", "num_institutes": "Nombre d'Instituts"},
                        title="Nombre d'Instituts Collaborés par Chercheur")
    st.plotly_chart(fig_collab, use_container_width=True)

# Visualisation 8 
with col2:
    fig_dashboard = go.Figure()

    for researcher in filtered_dashboard_data['researcher'].unique():
        researcher_data = filtered_dashboard_data[filtered_dashboard_data['researcher'] == researcher]
        researcher_data_sorted = researcher_data.sort_values(by='value of cited by', ascending=False)
        fig_dashboard.add_trace(go.Bar(
            x=researcher_data_sorted['value of cited by'],
            y=researcher_data_sorted['title'],
            name=researcher,
            orientation='h',
        ))

    fig_dashboard.update_layout(
        title="Top 5 Articles Most Cited per Researcher",
        xaxis=dict(title="Number of Citations"),
        yaxis=dict(title="Article Title", autorange="reversed"),
        barmode='group'
    )
    st.plotly_chart(fig_dashboard, use_container_width=True)

# Visualisation 9 
podium_fig = go.Figure()

podium_fig.add_trace(go.Bar(
    x=top_3_researchers['researcher'],  
    y=top_3_researchers['value of cited by'],  
    orientation='v',  
    marker=dict(color=['gold', 'silver', 'brown']), 
))

podium_fig.update_layout(
    title="Top 3 Researchers by Citations",
    xaxis=dict(title="Researcher"),  
    yaxis=dict(title="Total Citations"),  
    height=600  
)

st.plotly_chart(podium_fig, use_container_width=True)


