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
    
    # Ajouter les arêtes au graphe avec leurs poids
    for edge in tqdm(graph_data, desc="Ajout des arêtes au graphe", file=sys.stdout):
        source = edge["source"]
        target = edge["target"]
        weight = edge["weight"]
        G.add_edge(source, target, weight=weight)
    
    # Calculer les degrés de centralité pour influencer le placement des nœuds
    degree_centrality = nx.degree_centrality(G)
    # Normaliser pour que 0 soit le moins central et 1 le plus central
    max_centrality = max(degree_centrality.values()) if degree_centrality else 1
    for node in G.nodes():
        G.nodes[node]['centrality'] = degree_centrality[node] / max_centrality if max_centrality > 0 else 0
    
    # Utiliser un layout avec plus d'itérations et un k plus grand pour étaler davantage le graphe
    # Plus la valeur de k est grande, plus les nœuds seront espacés
    # 1.5 est une valeur qui donne un bon étalement sans être excessif
    pos = nx.spring_layout(G, weight='weight', k=1.5/math.sqrt(len(G.nodes())), 
                          iterations=200, seed=42)
    
    # Préparer les positions des nœuds
    x_nodes = [pos[node][0] for node in G.nodes()]
    y_nodes = [pos[node][1] for node in G.nodes()]
    
    # Préparer les données pour les arêtes
    edge_weights = [G.get_edge_data(u, v)['weight'] for u, v in G.edges()]
    max_weight = max(edge_weights) if edge_weights else 1
    min_weight = min(edge_weights) if edge_weights else 0
    
    # Créer des couleurs pour les arêtes basées sur leur poids (intensité de collaboration)
    edge_colors = []
    for weight in edge_weights:
        # Normaliser entre 0 et 1
        normalized = (weight - min_weight) / (max_weight - min_weight) if max_weight > min_weight else 0.5
        # Créer une couleur avec une intensité variable
        edge_colors.append(f"rgba(70, 130, 180, {0.3 + 0.7*normalized})")
    
    # Largeur des arêtes normalisée entre 0.5 et 5 selon le poids
    normalized_weights = [0.5 + 4.5 * ((weight - min_weight) / (max_weight - min_weight)) 
                         if max_weight > min_weight else 1 for weight in edge_weights]
    
    # Créer des traces distinctes pour chaque arête
    edge_traces = []
    i = 0
    for u, v in G.edges():
        edge_trace = go.Scatter(
            x=[pos[u][0], pos[v][0], None],
            y=[pos[u][1], pos[v][1], None],
            line=dict(width=normalized_weights[i], color=edge_colors[i]),
            hoverinfo="text",
            text=f"<b>{u} — {v}</b><br>{G.get_edge_data(u, v)['weight']} publications",
            mode="lines",
            opacity=0.8
        )
        edge_traces.append(edge_trace)
        i += 1
    
    # Calculer les tailles des nœuds basées sur leur centralité (nœuds importants plus grands)
    node_sizes = []
    node_colors = []
    node_texts = []
    
    for node in G.nodes():
        # Taille basée sur le nombre de connexions (de 15 à 50)
        size = 15 + 35 * G.nodes[node]['centrality']
        node_sizes.append(size)
        
        # Couleur basée sur la centralité (du plus foncé au plus clair)
        color_intensity = G.nodes[node]['centrality']
        node_colors.append(f"rgba(31, 119, 180, {0.6 + 0.4*color_intensity})")
        
        # Texte d'information
        connections = len(list(G.neighbors(node)))
        node_texts.append(f"<b>{node}</b><br>Collaborations: {connections}")
    
    # Tracer les nœuds avec une meilleure apparence
    node_trace = go.Scatter(
        x=x_nodes,
        y=y_nodes,
        mode="markers+text",
        hoverinfo="text",
        marker=dict(
            showscale=True,
            colorscale="Blues",
            reversescale=False,
            size=node_sizes,
            color=node_colors,
            colorbar=dict(
                thickness=15,
                title=dict(
                    text="Centralité",
                    font=dict(size=12)
                ),
                xanchor="left"
            ),
            line=dict(width=1, color="white")
        ),
        text=[node for node in G.nodes()],
        hovertext=node_texts,
        textposition="top center",
        textfont=dict(size=10, color="black", family="Arial"),
    )
    
    # Créer la figure avec une meilleure mise en page - TAILLE PLEINE PAGE
    fig_graph = go.Figure(
        data=edge_traces + [node_trace],
        layout=go.Layout(
            title=dict(
                text="Réseau de collaborations entre chercheurs",
                font=dict(size=20, color="#2c3e50", family="Arial"),
                x=0.5
            ),
            showlegend=False,
            hovermode="closest",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=900,       # Hauteur augmentée
            width=1400,       # Largeur augmentée pour occuper toute la page
            margin=dict(l=5, r=5, t=50, b=5),   # Marges minimales
            paper_bgcolor="white",
            plot_bgcolor="rgba(240,240,240,0.8)",
            annotations=[
                dict(
                    text=f"Nombre de chercheurs: {len(G.nodes())}<br>Nombre de collaborations: {len(G.edges())}",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.01, y=0.01,
                    font=dict(size=10, color="#7f7f7f"),
                    bgcolor="white",
                    borderpad=4
                )
            ]
        )
    )
    
    return fig_graph

