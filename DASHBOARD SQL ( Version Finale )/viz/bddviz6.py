import plotly.graph_objects as go
import mysql.connector
from mysql.connector import Error
import networkx as nx
import pandas as pd
from tqdm import tqdm
import sys
import math
import os 


# 🔹 1. Lire la liste de chercheurs autorisés
def lire_chercheurs_autorises(fichier):
    try:
        with open(fichier, "r", encoding="utf-8") as f:
            chercheurs = [ligne.strip() for ligne in f if ligne.strip()]
        return set(chercheurs)
    except FileNotFoundError:
        print(f"Fichier non trouvé : {fichier}")
        return set()

# 🔹 2. Récupérer le graphe de collaboration
def get_collaboration_network(chercheurs_autorises):
    try:
                # Configurer la connexion à la base de données
        connection = mysql.connector.connect(
        host=os.getenv("DB_HOST", "db"),
        user=os.getenv("DB_USER", "user"),
        password=os.getenv("DB_PASS", "userpass"),
        database=os.getenv("DB_NAME", "dashboarddb"),
        port=int(os.getenv("DB_PORT", "3306")))
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            query = """
            SELECT 
                CONCAT(c1.prenom, ' ', c1.nom) AS source,
                CONCAT(c2.prenom, ' ', c2.nom) AS target,
                COUNT(DISTINCT p1.publication_id) AS weight
            FROM publication_auteurs pa1
            JOIN chercheurs c1 ON pa1.chercheur_id = c1.chercheur_id
            JOIN publications p1 ON pa1.publication_id = p1.publication_id
            JOIN publication_auteurs pa2 ON p1.publication_id = pa2.publication_id AND pa1.chercheur_id != pa2.chercheur_id
            JOIN chercheurs c2 ON pa2.chercheur_id = c2.chercheur_id
            WHERE c1.chercheur_id < c2.chercheur_id
            GROUP BY c1.chercheur_id, c2.chercheur_id
            HAVING COUNT(DISTINCT p1.publication_id) > 0
            ORDER BY COUNT(DISTINCT p1.publication_id) DESC
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            connection.close()
            
            # 🔹 3. Filtrer selon les noms autorisés
            filtered_results = [
                edge for edge in results
                if edge["source"] in chercheurs_autorises and edge["target"] in chercheurs_autorises
            ]
            return filtered_results
            
    except Error as e:
        print(f"Erreur lors de la connexion à MySQL: {e}")
        return []
    
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

# 🔹 4. Création du graphe avec une visualisation améliorée
def create_enhanced_network_graph():
    chercheurs_autorises = lire_chercheurs_autorises("researchers.txt")
    graph_data = get_collaboration_network(chercheurs_autorises)
    
    if not graph_data:
        print("Aucune donnée de collaboration trouvée.")
        return None
    
    G = nx.Graph()
    for edge in tqdm(graph_data, desc="Ajout des arêtes au graphe", file=sys.stdout):
        source, target, weight = edge["source"], edge["target"], edge["weight"]
        G.add_edge(source, target, weight=weight)
    
    degree_centrality = nx.degree_centrality(G)
    max_centrality = max(degree_centrality.values()) or 1
    for node in G.nodes():
        G.nodes[node]['centrality'] = degree_centrality[node] / max_centrality

    pos = nx.spring_layout(G, weight='weight', k=20, iterations=300, seed=42)

    edge_traces = []
    edge_weights = [G[u][v]['weight'] for u, v in G.edges()]
    max_weight = max(edge_weights) or 1
    min_weight = min(edge_weights)

    for i, (u, v) in enumerate(G.edges()):
        weight = G[u][v]['weight']
        norm_weight = (weight - min_weight) / (max_weight - min_weight) if max_weight > min_weight else 0.5
        color = f"rgba(100, 100, 250, {0.2 + 0.6 * norm_weight})"
        width = 0.5 + 5 * norm_weight

        edge_traces.append(go.Scatter(
            x=[pos[u][0], pos[v][0], None],
            y=[pos[u][1], pos[v][1], None],
            line=dict(width=width, color=color),
            mode="lines",
            hoverinfo="text",
            text=f"<b>{u} ↔ {v}</b><br>{weight} co-publications",
            opacity=0.8
        ))

    x_nodes = [pos[node][0] for node in G.nodes()]
    y_nodes = [pos[node][1] for node in G.nodes()]
    node_sizes = []
    node_colors = []
    node_texts = []

    for node in G.nodes():
        centrality = G.nodes[node]['centrality']
        size = 18 + 30 * centrality
        node_sizes.append(size)
        node_colors.append(centrality)
        node_texts.append(f"<b>{node}</b><br>Centralité : {centrality:.2f}<br>Liens : {G.degree[node]}")

    # Tracer les nœuds sans nom visible par défaut
    node_trace = go.Scatter(
        x=x_nodes,
        y=y_nodes,
        mode="markers",
        hovertext=node_texts,
        hoverinfo="text",
        marker=dict(
            showscale=True,
            colorscale="YlGnBu",
            reversescale=False,
            color=node_colors,
            size=node_sizes,
            colorbar=dict(
                thickness=15,
                title="Centralité",
                xanchor="left"
            ),
            line=dict(width=1, color='white')
        )
    )

    fig_graph = go.Figure(
        data=edge_traces + [node_trace],
        layout=go.Layout(
            showlegend=False,
            hovermode="closest",
            margin=dict(l=10, r=10, t=60, b=10),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=2000,
            width=3600,
            paper_bgcolor="white",
            plot_bgcolor="rgba(245, 247, 250, 0.95)",
            annotations=[
                dict(
                    text=f"👥 {len(G.nodes())} chercheurs — 🔁 {len(G.edges())} collaborations",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.01, y=0.01,
                    font=dict(size=11, color="gray"),
                    bgcolor="white",
                    borderpad=4
                )
            ]
        )
    )

    return fig_graph
