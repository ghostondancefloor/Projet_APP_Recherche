import json
import networkx as nx
import plotly.graph_objects as go
import streamlit as st

# Charger les données depuis le fichier JSON
with open('graph_edges.json', 'r', encoding='utf-8') as f:
    graph_data = json.load(f)

# Créer un graphe NetworkX
G = nx.Graph()

# Ajouter les arêtes au graphe (avec poids)
for edge in graph_data:
    source = edge['source']
    target = edge['target']
    weight = edge['weight']
    G.add_edge(source, target, weight=weight)

# Obtenir les positions des nœuds via un layout (Spring Layout)
pos = nx.spring_layout(G, seed=42)  # 'seed' pour reproductibilité des positions

# Extraire les coordonnées des nœuds
x_nodes = [pos[node][0] for node in G.nodes()]
y_nodes = [pos[node][1] for node in G.nodes()]

# Extraire les coordonnées des arêtes
x_edges = []
y_edges = []
for edge in G.edges():
    x_edges.append(pos[edge[0]][0])
    x_edges.append(pos[edge[1]][0])
    y_edges.append(pos[edge[0]][1])
    y_edges.append(pos[edge[1]][1])

# Créer les arêtes dans Plotly
edge_trace = go.Scatter(
    x=x_edges, y=y_edges,
    line=dict(width=0.5, color='gray'),
    hoverinfo='none',
    mode='lines'
)

# Créer les nœuds dans Plotly
node_trace = go.Scatter(
    x=x_nodes, y=y_nodes,
    mode='markers',
    hoverinfo='text',
    marker=dict(
        showscale=True,
        colorscale='YlGnBu',
        size=10,
        colorbar=dict(
            thickness=15,
            title='Node Connections',
            xanchor='left',
            titleside='right'
        )
    )
)

# Ajouter des informations au survol des nœuds
node_text = []
for node in G.nodes():
    node_text.append(node)  # Affiche le nom du chercheur survolé

node_trace.marker.color = [len(list(G.neighbors(node))) for node in G.nodes()]
node_trace.text = node_text

# Créer la figure avec les arêtes et les nœuds sans le bouton "Reset"
fig = go.Figure(data=[edge_trace, node_trace],
                layout=go.Layout(
                    showlegend=False,
                    hovermode='closest',
                    title="Collaborations entre Chercheurs",
                    xaxis=dict(showgrid=False, zeroline=False),
                    yaxis=dict(showgrid=False, zeroline=False)
                ))

# Afficher le graphique avec Streamlit
st.title("Graphique des Collaborations Internes entre Chercheurs Listic")
st.plotly_chart(fig)
