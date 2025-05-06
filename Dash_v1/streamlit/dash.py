import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import random
import networkx as nx
import requests
from datetime import datetime

# Configuration de l'application
st.set_page_config(layout="wide")

# Configuration de l'API
API_URL = "http://api_service:8000"  # Utilisez le nom du service Docker
API_USERNAME = "admin"
API_PASSWORD = "password"

# Authentification API avec gestion des erreurs améliorée
@st.cache_resource
def get_api_token():
    try:
        response = requests.post(
            f"{API_URL}/token",
            data={"username": API_USERNAME, "password": API_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        response.raise_for_status()
        return response.json().get("access_token")
    except requests.exceptions.RequestException as e:
        st.error(f"Erreur de connexion à l'API: {str(e)}")
        st.stop()
    except Exception as e:
        st.error(f"Erreur inattendue: {str(e)}")
        st.stop()

# Appels API avec cache et gestion des erreurs
@st.cache_data(ttl=300)
def call_api(endpoint):
    token = get_api_token()
    try:
        response = requests.get(
            f"{API_URL}/{endpoint}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        st.error(f"Erreur API ({endpoint}): {e.response.status_code}")
        return []
    except Exception as e:
        st.error(f"Erreur lors de l'appel à {endpoint}: {str(e)}")
        return []

# Récupération des données
def load_all_data():
    try:
        stats_pays_data = call_api("api/stats_pays")
        chercheurs_data = call_api("api/chercheurs")
        publications_data = call_api("api/publications")
        institutions_data = call_api("api/institutions")
        collaborations_data = call_api("api/collaborations")
        sankey_data = call_api("api/sankey")
        graph_data = call_api("api/graph")
        
        return {
            "stats_pays": stats_pays_data,
            "chercheurs": chercheurs_data,
            "publications": publications_data,
            "institutions": institutions_data,
            "collaborations": collaborations_data,
            "sankey": sankey_data,
            "graph": graph_data
        }
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {str(e)}")
        st.stop()

data = load_all_data()

# Préparation des DataFrames
def prepare_dataframes(data):
    # DataFrame stats pays
    df = pd.DataFrame([
        {
            "year": entry.get("annee"), 
            "country": entry.get("pays"), 
            "count": 0 if entry.get("pays") == "France" else entry.get("nombre_publications", 0)
        }
        for entry in data["stats_pays"]
        if entry.get("annee") and entry.get("pays")
    ])
    df["year"] = df["year"].astype(str)

    # DataFrame publications par chercheur
    publications_list = []
    for chercheur in data["chercheurs"]:
        nom = chercheur.get("nom")
        for pub in chercheur.get("publications", []):
            if pub.get("titre") and pub.get("citations") is not None:
                publications_list.append({
                    "researcher": nom,
                    "title": pub.get("titre"),
                    "year": pub.get("annee"),
                    "value of cited by": pub.get("citations")
                })
    
    dashboard_df = pd.DataFrame(publications_list)

    # DataFrame publications par date
    all_pubs = []
    for pub in data["publications"]:
        annee = pub.get("annee")
        if annee:
            for auteur in pub.get("auteurs", []):
                all_pubs.append({
                    "customAuthorName": auteur,
                    "publicationDate_s": f"{annee}-01-01",
                    "title": pub.get("titre"),
                    "citations": pub.get("citations")
                })
    
    df1 = pd.DataFrame(all_pubs)
    df2 = df1.copy()

    # Format des dates
    def preprocess_dates(date_str):
        if pd.isna(date_str): return None
        if len(date_str) == 4: return f"{date_str}-01-01"
        if len(date_str) == 7: return f"{date_str}-01"
        return date_str

    for df_tmp in [df1, df2]:
        df_tmp["publicationDate_s"] = pd.to_datetime(
            df_tmp["publicationDate_s"].apply(preprocess_dates), 
            errors="coerce"
        )
        df_tmp["publicationYear"] = df_tmp["publicationDate_s"].dt.year
        df_tmp["publicationMonth"] = df_tmp["publicationDate_s"].dt.to_period("M")

    return {
        "df": df,
        "dashboard_df": dashboard_df,
        "df1": df1,
        "df2": df2,
        "sankey_data": data["sankey"],
        "graph_data": data["graph"],
        "chercheurs_data": data["chercheurs"]
    }

dfs = prepare_dataframes(data)

# Fonctions utilitaires
def analyze_data(professor_name, start_year, end_year):
    universities = []
    for chercheur in dfs["chercheurs_data"]:
        if chercheur["nom"].lower() == professor_name.lower():
            for pub in chercheur.get("publications", []):
                if pub.get("annee") and start_year <= int(pub["annee"]) <= end_year:
                    universities.extend(chercheur.get("institutions", []))
    return Counter(universities).most_common(10)

def generate_colors(labels):
    random.seed(42)
    return {label: f"rgba({random.randint(0,255)}, {random.randint(0,255)}, {random.randint(0,255)}, 0.8)" 
            for label in labels}

def generate_sankey(chercheur_name):
    data = [entry for entry in dfs["sankey_data"] if entry["source"] == chercheur_name]
    if not data:
        return None
    
    sources, targets, values, labels, label_map = [], [], [], [], {}
    idx = 0
    
    for entry in data:
        for key in [entry["source"], entry["target"]]:
            if key not in label_map:
                label_map[key] = idx
                labels.append(key)
                idx += 1
        sources.append(label_map[entry["source"]])
        targets.append(label_map[entry["target"]])
        values.append(entry["value"])
    
    color_map = generate_colors(labels)
    
    fig = go.Figure(go.Sankey(
        node=dict(
            label=labels,
            pad=20,
            thickness=20,
            line=dict(color="black", width=0.5),
            color=[color_map[l] for l in labels]
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=[color_map[labels[t]] for t in targets]
        )
    ))
    
    fig.update_layout(
        title_text=f"Collaborations de {chercheur_name}",
        font_size=12,
        height=700
    )
    return fig

def create_network_graph():
    if not dfs["graph_data"]:
        return None
    
    G = nx.Graph()
    for edge in dfs["graph_data"]:
        G.add_edge(edge["source"], edge["target"], weight=edge["weight"])
    
    if len(G.nodes()) == 0:
        return None
    
    pos = nx.spring_layout(G, k=0.3, iterations=50, seed=42)
    
    # Edge traces
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')
    
    # Node traces
    node_x = []
    node_y = []
    node_text = []
    node_adjacencies = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        connections = len(list(G.neighbors(node)))
        node_text.append(f"{node}<br>Connections: {connections}")
        node_adjacencies.append(connections)
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        textposition='top center',
        hovertext=node_text,
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            size=15,
            color=node_adjacencies,
            colorbar=dict(
                thickness=15,
                title='Connections',
                xanchor='left'
            ),
            line_width=2))
    
    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            title_text='Réseau de collaborations'
        )
    )
    
    fig.update_layout(height=700)
    return fig

# Interface utilisateur
st.sidebar.title("Filtres")

# Gestion des pages
if "page" not in st.session_state:
    st.session_state.page = 1

def next_page():
    if st.session_state.page < 2:
        st.session_state.page += 1

def previous_page():
    if st.session_state.page > 1:
        st.session_state.page -= 1

# Configuration des filtres
if not dfs["df"].empty and 'year' in dfs["df"].columns:
    years = sorted(dfs["df"]["year"].unique())
    selected_year = st.sidebar.slider(
        "Sélectionnez une année",
        min_value=int(min(years)) if years else 2000,
        max_value=int(max(years)) if years else 2023,
        value=int(min(years)) if years else 2000
    )
else:
    selected_year = 2000

if not dfs["df1"].empty and 'publicationYear' in dfs["df1"].columns:
    pub_years = [y for y in dfs["df1"]["publicationYear"].unique() if not pd.isna(y)]
    if pub_years:
        start_year, end_year = st.sidebar.slider(
            "Période de publication",
            min_value=int(min(pub_years)),
            max_value=int(max(pub_years)),
            value=(int(min(pub_years)), int(max(pub_years)))
        )
    else:
        start_year, end_year = 2000, 2023
else:
    start_year, end_year = 2000, 2023

# Sélection du chercheur
if not dfs["dashboard_df"].empty:
    all_researchers = sorted(set(dfs["dashboard_df"]["researcher"].dropna().unique()))
    selected_researcher = st.sidebar.selectbox(
        "Sélectionnez un chercheur",
        all_researchers if all_researchers else ["Aucun chercheur trouvé"]
    )
else:
    selected_researcher = "Aucun chercheur trouvé"


# Affichage principal
st.title("Analyse des publications scientifiques")

if st.session_state.page == 1:
    # Carte des pays collaborateurs
    if not dfs["df"].empty:
        filtered_df = dfs["df"][dfs["df"]["year"] == str(selected_year)]
        filtered_df_map = filtered_df[filtered_df["country"] != "France"]

        if not filtered_df_map.empty:
            fig_map = px.choropleth(
                filtered_df_map,
                locations="country",
                locationmode="country names",
                color="count",
                hover_name="country",
                title=f"Carte des pays collaborateurs en {selected_year}",
                color_continuous_scale="Plasma"
            )

            fig_map.add_scattergeo(
                locations=["France"],
                locationmode="country names",
                marker=dict(color="black", size=15),
                name="France"
            )
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.warning(f"Aucune donnée disponible pour {selected_year}")
    
    # Top 5 des pays collaborateurs
    if not dfs["df"].empty:
        filtered_df = dfs["df"][dfs["df"]["year"] == str(selected_year)]
        if not filtered_df.empty:
            top_5 = filtered_df.nlargest(5, "count")
            fig_bar = px.bar(
                top_5,
                x="country",
                y="count",
                text="count",
                title=f"Top 5 des pays collaborateurs en {selected_year}"
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    
    # Graphe de collaborations
    network_fig = create_network_graph()
    if network_fig:
        st.plotly_chart(network_fig, use_container_width=True)
    else:
        st.warning("Données de collaboration indisponibles")

elif st.session_state.page == 2:
    # Diagramme Sankey
    sankey_fig = generate_sankey(selected_researcher)
    if sankey_fig:
        st.plotly_chart(sankey_fig, use_container_width=True)
    else:
        st.warning(f"Pas de données de collaboration pour {selected_researcher}")
    
    # Publications par année
    if not dfs["df1"].empty:
        filtered_df1 = dfs["df1"][
            (dfs["df1"]["publicationYear"] >= start_year) & 
            (dfs["df1"]["publicationYear"] <= end_year)
        ]
        if selected_researcher != "Aucun chercheur trouvé":
            filtered_df1 = filtered_df1[filtered_df1["customAuthorName"] == selected_researcher]
        
        if not filtered_df1.empty:
            pub_count = filtered_df1.groupby("publicationYear").size().reset_index(name="count")
            fig_pub = px.bar(
                pub_count,
                x="publicationYear",
                y="count",
                title=f"Publications de {selected_researcher}"
            )
            st.plotly_chart(fig_pub, use_container_width=True)
    # --- Visualisation 8: Top 5 Articles Most Cited per Researcher ---
    if not dfs["dashboard_df"].empty:
        if selected_researcher != "Aucun chercheur trouvé":
            top_articles = dfs["dashboard_df"][
                dfs["dashboard_df"]["researcher"] == selected_researcher
            ].sort_values(by="value of cited by", ascending=False).head(5)

            if not top_articles.empty:
                fig_top_articles = px.bar(
                    top_articles,
                    x="value of cited by",
                    y="title",
                    orientation="h",
                    title=f"Top 5 Articles les Plus Cités de {selected_researcher}",
                    labels={"value of cited by": "Citations", "title": "Titre de l'article"},
                )
                fig_top_articles.update_layout(yaxis=dict(autorange="reversed"))
                st.plotly_chart(fig_top_articles, use_container_width=True)

    # --- Visualisation 9: Top 3 Researchers by Total Citations ---
    if not dfs["dashboard_df"].empty:
        top_3 = (
            dfs["dashboard_df"]
            .groupby("researcher")["value of cited by"]
            .sum()
            .reset_index()
            .sort_values(by="value of cited by", ascending=False)
            .head(3)
        )

        if not top_3.empty:
            fig_top3 = go.Figure(
                go.Bar(
                    x=top_3["researcher"],
                    y=top_3["value of cited by"],
                    marker=dict(color=["gold", "silver", "brown"]),
                )
            )
            fig_top3.update_layout(
                title="Top 3 Chercheurs par Citations",
                xaxis_title="Chercheur",
                yaxis_title="Nombre de Citations",
                height=500,
            )
            st.plotly_chart(fig_top3, use_container_width=True)

    # --- Visualisation 7: Number of Institutes per Researcher ---
    if dfs["sankey_data"]:
        collab_count = {}
        for entry in dfs["sankey_data"]:
            source = entry["source"]
            target = entry["target"]
            collab_count.setdefault(source, set()).add(target)

        collab_df = pd.DataFrame(
            [{"researcher": k, "num_institutes": len(v)} for k, v in collab_count.items()]
        )

        if not collab_df.empty:
            fig_inst = px.bar(
                collab_df.sort_values(by="num_institutes", ascending=False),
                x="researcher",
                y="num_institutes",
                title="Nombre d'Instituts Collaborés par Chercheur",
                labels={"researcher": "Chercheur", "num_institutes": "Instituts"},
            )
            st.plotly_chart(fig_inst, use_container_width=True)

    # --- Visualisation 4: Top Universities by Researcher (Pie Chart) ---
    if selected_researcher != "Aucun chercheur trouvé":
        university_counts = analyze_data(selected_researcher, start_year, end_year)
        if university_counts:
            df_uni = pd.DataFrame(university_counts, columns=["Université", "Nombre"])
            fig_pie = px.pie(
                df_uni,
                names="Université",
                values="Nombre",
                title=f"Top Universités pour {selected_researcher}",
            )
            st.plotly_chart(fig_pie, use_container_width=True)

# Navigation
col1, col2 = st.columns([1, 1])
with col1:
    if st.session_state.page > 1:
        st.button("← Page précédente", on_click=previous_page)
with col2:
    if st.session_state.page < 2:
        st.button("Page suivante →", on_click=next_page)