import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import random
import networkx as nx
from pymongo import MongoClient
from datetime import datetime

st.set_page_config(layout="wide")

# Ensuite, vous pouvez définir les fonctions et charger les données
@st.cache_resource
def get_mongodb_connection():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["research_db_structure"]
    return db

# Fonction pour récupérer les données depuis MongoDB
@st.cache_data
def get_stats_pays_data():
    db = get_mongodb_connection()
    # Récupérer les données de la collection stats_pays
    data = list(db.stats_pays.find({}, {"_id": 0}))
    return data

@st.cache_data
def get_chercheurs_data():
    db = get_mongodb_connection()
    # Récupérer les données de la collection chercheurs
    data = list(db.chercheurs.find({}, {"_id": 0}))
    return data

@st.cache_data
def get_publications_data():
    db = get_mongodb_connection()
    # Récupérer les données de la collection publications
    data = list(db.publications.find({}, {"_id": 0}))
    return data

@st.cache_data
def get_institutions_data():
    db = get_mongodb_connection()
    # Récupérer les données de la collection institutions
    data = list(db.institutions.find({}, {"_id": 0}))
    return data

@st.cache_data
def get_collaborations_data():
    db = get_mongodb_connection()
    # Récupérer les données de la collection collaborations
    data = list(db.collaborations.find({}, {"_id": 0}))
    return data

# Récupération des données
stats_pays_data = get_stats_pays_data()
chercheurs_data = get_chercheurs_data()
publications_data = get_publications_data()
institutions_data = get_institutions_data()
collaborations_data = get_collaborations_data()

# Conversion des données pays en dataframe
rows = []
for entry in stats_pays_data:
    year = entry.get("annee")
    pays = entry.get("pays")
    nombre_publications = entry.get("nombre_publications")
    
    # Traitement spécial pour la France si nécessaire
    if pays == "France":
        rows.append({"year": year, "country": pays, "count": 0})
    else:
        rows.append({"year": year, "country": pays, "count": nombre_publications})

df = pd.DataFrame(rows)

# Création d'un dataframe pour les publications par chercheur
publications_df = []
for chercheur in chercheurs_data:
    nom_chercheur = chercheur.get("nom")
    for publication in chercheur.get("publications", []):
        titre = publication.get("titre")
        annee = publication.get("annee")
        citations = publication.get("citations")
        if titre and citations is not None:
            publications_df.append({
                "researcher": nom_chercheur,
                "title": titre,
                "year": annee,
                "value of cited by": citations
            })

dashboard_df = pd.DataFrame(publications_df)

# Créer un dataframe avec les dates de publication
all_pubs = []
for pub in publications_data:
    annee_str = str(pub.get("annee")) if pub.get("annee") else None
    auteurs = pub.get("auteurs", [])
    for auteur in auteurs:
        if annee_str:
            date_str = f"{annee_str}-01-01"  # Utiliser le premier jour de l'année
            all_pubs.append({
                "customAuthorName": auteur,
                "publicationDate_s": date_str,
                "title": pub.get("titre"),
                "citations": pub.get("citations")
            })

df1 = pd.DataFrame(all_pubs)
df2 = df1.copy()  # Copie pour rester compatible avec le code original

# Prétraitement des dates
def preprocess_dates(date_str):
    if pd.isna(date_str):
        return None
    if len(date_str) == 4:
        return f"{date_str}-01-01"
    elif len(date_str) == 7:
        return f"{date_str}-01"
    return date_str

for df_tmp in [df1, df2]:
    df_tmp["publicationDate_s"] = df_tmp["publicationDate_s"].apply(preprocess_dates)
    df_tmp["publicationDate_s"] = pd.to_datetime(df_tmp["publicationDate_s"], errors="coerce")
    df_tmp["publicationYear"] = df_tmp["publicationDate_s"].dt.year
    df_tmp["publicationMonth"] = df_tmp["publicationDate_s"].dt.to_period("M")

# Créer des données Sankey
def create_sankey_data():
    sankey_data = []
    for chercheur in chercheurs_data:
        nom_chercheur = chercheur.get("nom")
        institutions = chercheur.get("institutions", [])
        for institution in institutions:
            # Pour simplifier, on utilise un poids fixe, ou vous pourriez calculer un poids basé sur d'autres facteurs
            sankey_data.append({
                "source": nom_chercheur,
                "target": institution,
                "value": 1  # Valeur par défaut, peut être ajustée
            })
    return sankey_data

sankey_data = create_sankey_data()

# Créer des données pour le graphe
def create_graph_data():
    graph_data = []
    for collab in collaborations_data:
        source = collab.get("chercheur1")
        target = collab.get("chercheur2")
        weight = collab.get("poids")
        if source and target and weight:
            graph_data.append({
                "source": source,
                "target": target,
                "weight": weight
            })
    return graph_data

graph_data = create_graph_data()

def analyze_data(professor_name, start_year, end_year):
    universities = []
    for chercheur in chercheurs_data:
        if chercheur["nom"].lower() == professor_name.lower():
            for publication in chercheur.get("publications", []):
                publication_year = publication.get("annee")
                if publication_year and start_year <= int(publication_year) <= end_year:
                    universities.extend(chercheur.get("institutions", []))
    return Counter(universities).most_common(10)

def generate_colors(labels):
    random.seed(42)
    return {
        label: f"rgba({random.randint(0,255)}, {random.randint(0,255)}, {random.randint(0,255)}, 0.8)"
        for label in labels
    }

def generate_sankey(chercheur_name):
    sources, targets, values, labels = [], [], [], []
    label_map, current_index = {}, 0

    filtered_sankey = [entry for entry in sankey_data if entry["source"] == chercheur_name]
    
    for entry in filtered_sankey:
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

    fig = go.Figure(
        data=[
            go.Sankey(
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
                    color=[color_map[labels[t]] for t in targets] if targets else [],
                ),
            )
        ]
    )

    fig.update_layout(
        title_text=f"Diagramme de Sankey pour {chercheur_name}",
        font=dict(size=12, color="black", family="Arial"),
        height=700,
        width=1000,
        margin=dict(l=0, r=0, t=40, b=40),
    )
    return fig

st.sidebar.title("Filtres")

if "page" not in st.session_state:
    st.session_state.page = 1

def next_page():
    if st.session_state.page < 2:
        st.session_state.page += 1

def previous_page():
    if st.session_state.page > 1:
        st.session_state.page -= 1

# Configuration des filtres
if not df.empty and 'year' in df.columns:
    years = sorted(df["year"].unique())
    selected_year = st.sidebar.slider(
        "Sélectionnez une année",
        min_value=int(min(years)) if years else 2000,
        max_value=int(max(years)) if years else 2023,
        value=int(min(years)) if years else 2000,
        step=1,
    )
else:
    selected_year = 2000
    years = [2000]

if not df1.empty and 'publicationYear' in df1.columns:
    publication_years_min = int(df1["publicationYear"].min()) if not df1["publicationYear"].isna().all() else 2000
    publication_years_max = int(df1["publicationYear"].max()) if not df1["publicationYear"].isna().all() else 2023
    
    start_year, end_year = st.sidebar.slider(
        "Période de publication",
        min_value=publication_years_min,
        max_value=publication_years_max,
        value=(publication_years_min, publication_years_max),
        step=1,
    )
else:
    start_year, end_year = 2000, 2023

# Traitement des données pour le dashboard
if not dashboard_df.empty:
    top_articles_per_researcher = (
        dashboard_df.groupby(["researcher", "title"])["value of cited by"]
        .sum()
        .reset_index()
    )

    top_articles_per_researcher = top_articles_per_researcher.sort_values(
        by=["researcher", "value of cited by"], ascending=[True, False]
    )

    top_5_articles = top_articles_per_researcher.groupby("researcher").head(5)

    total_citations_per_researcher = (
        dashboard_df.groupby("researcher")["value of cited by"].sum().reset_index()
    )

    total_citations_per_researcher = total_citations_per_researcher.sort_values(
        by="value of cited by", ascending=False
    )

    top_3_researchers = total_citations_per_researcher.head(3)

    researcher_list = list(top_5_articles["researcher"].unique()) if not top_5_articles.empty else ["Aucun chercheur trouvé"]
    selected_dashboard_researcher = st.sidebar.selectbox(
        "Sélectionnez un chercheur pour le dashboard supplémentaire",
        researcher_list
    )

    filtered_dashboard_data = top_5_articles[
        top_5_articles["researcher"] == selected_dashboard_researcher
    ] if selected_dashboard_researcher in researcher_list else pd.DataFrame()
else:
    filtered_dashboard_data = pd.DataFrame()
    top_3_researchers = pd.DataFrame(columns=["researcher", "value of cited by"])
    researcher_list = ["Aucun chercheur trouvé"]
    selected_dashboard_researcher = researcher_list[0]

# -------------------------------------------------------

st.title("Analyse des publications scientifiques")
st.title("        ")

# -------------------------------------------------------

if st.session_state.page == 1:
    # Visualisation 1
    filtered_df = df[df["year"] == str(selected_year)]
    if not filtered_df.empty:
        fig_map = px.choropleth(
            filtered_df,
            locations="country",
            locationmode="country names",
            color="count",
            hover_name="country",
            title=f"Carte des pays collaborateurs en {selected_year}",
            color_continuous_scale="Plasma",
            labels={"count": "Nombre", "country": "Pays"},
        )
        fig_map.add_scattergeo(
            locations=["France"],
            locationmode="country names",
            marker=dict(color="black", size=15),
            name="France (Noire)",
        )
        fig_map.update_layout(
            height=700, width=1200, margin={"r": 0, "t": 50, "l": 0, "b": 0}
        )
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning(f"Aucune donnée disponible pour l'année {selected_year}")

    # Visualisation 2
    if not filtered_df.empty:
        top_5 = filtered_df.sort_values(by="count", ascending=False).head(5)
        fig_bar = px.bar(
            top_5,
            x="country",
            y="count",
            text="count",
            title=f"Top 5 des pays collaborateurs {selected_year}",
            labels={"count": "Nombre", "country": "Pays"},
        )
        fig_bar.update_traces(textposition="outside")
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.warning(f"Aucune donnée disponible pour l'année {selected_year}")

    # Visualisation 6 - Graphe de collaborations
    if graph_data:
        G = nx.Graph()

        for edge in graph_data:
            source = edge["source"]
            target = edge["target"]
            weight = edge["weight"]
            G.add_edge(source, target, weight=weight)

        if G.number_of_nodes() > 0:
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
                mode="lines",
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
                        title=dict(
                            text="Node Connections"
                        ),
                        xanchor="left"
                    )
                )
            )

            node_text = [f"{node}" for node in G.nodes()]
            node_trace.marker.color = [len(list(G.neighbors(node))) for node in G.nodes()]
            node_trace.text = node_text

            fig_graph = go.Figure(
                data=[edge_trace, node_trace],
                layout=go.Layout(
                    showlegend=False,
                    hovermode="closest",
                    title="Collaborations entre Chercheurs",
                    xaxis=dict(showgrid=False, zeroline=False),
                    yaxis=dict(showgrid=False, zeroline=False),
                ),
            )
            st.plotly_chart(fig_graph, use_container_width=True)
        else:
            st.warning("Pas suffisamment de données pour créer le graphe de collaborations")
    else:
        st.warning("Aucune donnée de collaboration disponible")

    # Visualisation 7 - Nombre d'instituts par chercheur
    if sankey_data:
        collab_count = {}

        for entry in sankey_data:
            source = entry["source"]
            target = entry["target"]
            if source not in collab_count:
                collab_count[source] = set()
            collab_count[source].add(target)

        collab_data = [
            {"professor": prof, "num_institutes": len(instituts)}
            for prof, instituts in collab_count.items()
        ]
        collab_df = pd.DataFrame(collab_data)

        if not collab_df.empty:
            fig_collab = px.bar(
                collab_df,
                x="professor",
                y="num_institutes",
                labels={
                    "professor": "Nom du Professeur",
                    "num_institutes": "Nombre d'Instituts",
                },
                title="Nombre d'Instituts Collaborés par Chercheur",
            )
            st.plotly_chart(fig_collab, use_container_width=True)
        else:
            st.warning("Aucune donnée de collaboration avec des instituts disponible")
    else:
        st.warning("Aucune donnée de collaboration disponible")

    # Visualisation 9 - Top 3 chercheurs par citations
    if not top_3_researchers.empty:
        podium_fig = go.Figure()

        podium_fig.add_trace(
            go.Bar(
                x=top_3_researchers["researcher"],
                y=top_3_researchers["value of cited by"],
                orientation="v",
                marker=dict(color=["gold", "silver", "brown"]),
            )
        )

        podium_fig.update_layout(
            title="Top 3 Researchers by Citations",
            xaxis=dict(title="Researcher"),
            yaxis=dict(title="Total Citations"),
            height=600,
        )

        st.plotly_chart(podium_fig, use_container_width=True)
    else:
        st.warning("Aucune donnée de citation disponible")

elif st.session_state.page == 2:
    # Visualisation 8 - Articles les plus cités par chercheur
    if not filtered_dashboard_data.empty:
        fig_dashboard = go.Figure()

        for researcher in filtered_dashboard_data["researcher"].unique():
            researcher_data = filtered_dashboard_data[
                filtered_dashboard_data["researcher"] == researcher
            ]
            researcher_data_sorted = researcher_data.sort_values(
                by="value of cited by", ascending=False
            )
            fig_dashboard.add_trace(
                go.Bar(
                    x=researcher_data_sorted["value of cited by"],
                    y=researcher_data_sorted["title"],
                    name=researcher,
                    orientation="h",
                )
            )

        fig_dashboard.update_layout(
            title="Top 5 Articles Most Cited per Researcher",
            xaxis=dict(title="Number of Citations"),
            yaxis=dict(title="Article Title", autorange="reversed"),
            barmode="group",
        )
        st.plotly_chart(fig_dashboard, use_container_width=True)
    else:
        st.warning(f"Aucune donnée disponible pour {selected_dashboard_researcher}")

    # Visualisation 3 - Publications par année
    filtered_df1 = df1[
        (df1["publicationYear"] >= start_year) & (df1["publicationYear"] <= end_year)
    ]
    if selected_dashboard_researcher != "All Researchers" and selected_dashboard_researcher != "Aucun chercheur trouvé":
        filtered_df1 = filtered_df1[
            filtered_df1["customAuthorName"] == selected_dashboard_researcher
        ]
    
    if not filtered_df1.empty:
        publication_count_by_year = (
            filtered_df1.groupby("publicationYear").size().reset_index(name="count")
        )
        fig_pub = px.bar(
            publication_count_by_year,
            x="publicationYear",
            y="count",
            title=(
                f"Publications de {selected_dashboard_researcher}"
                if selected_dashboard_researcher != "All Researchers" and selected_dashboard_researcher != "Aucun chercheur trouvé"
                else "Publications par année"
            ),
            labels={"publicationYear": "Année", "count": "Nombre de publications"},
        )
        st.plotly_chart(fig_pub, use_container_width=True)
    else:
        st.warning(f"Aucune publication trouvée pour la période sélectionnée")

    # Diagramme Sankey
    if selected_dashboard_researcher != "Aucun chercheur trouvé" and sankey_data:
        fig_sankey = generate_sankey(selected_dashboard_researcher)
        st.plotly_chart(fig_sankey, use_container_width=True)
    else:
        st.warning(f"Aucune donnée de collaboration disponible pour {selected_dashboard_researcher}")

    # Visualisation 4 - Top Universités pour un chercheur
    if selected_dashboard_researcher != "Aucun chercheur trouvé":
        university_counts = analyze_data(selected_dashboard_researcher, start_year, end_year)
        if university_counts:
            df_chart = {
                "University": [item[0] for item in university_counts],
                "Count": [item[1] for item in university_counts],
            }
            fig_pie = px.pie(
                df_chart,
                names="University",
                values="Count",
                title=f"Top 10 Universités pour {selected_dashboard_researcher}",
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.warning(
                f"Aucune publication trouvée pour {selected_dashboard_researcher} entre {start_year} et {end_year}."
            )
    else:
        st.warning("Aucun chercheur sélectionné")

col_prev, col_spacer, col_next = st.columns([2, 6, 2])

with col_prev:
    if st.session_state.page > 1:
        st.button("← Page précédente", on_click=previous_page)

with col_next:
    if st.session_state.page < 2:
        st.button("Page suivante →", on_click=next_page)