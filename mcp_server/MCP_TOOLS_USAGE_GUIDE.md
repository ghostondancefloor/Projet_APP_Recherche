# Guide d'utilisation des outils MCP dans dash.py

## Vue d'ensemble

Les outils MCP (Model Context Protocol) sont définis dans `mcp_server/researchMCPServer.py` et sont accessibles via `MCPServiceManager` dans `mcp_server/mcp_service.py`.

## 🎯 Méthodes d'accès aux outils MCP

### 1. **Via le Chat Assistant (Déjà implémenté)**

```python
from mcp_server.mcp_service import get_mcp_manager

# Dans dash.py
mcp = get_mcp_manager()
response = mcp.query("Quelles sont les statistiques globales ?")
# Le LLM interprète la question et appelle l'outil approprié
```

### 2. **Appel Direct des Outils**

```python
from mcp_server.mcp_service import get_mcp_manager

# Obtenir le gestionnaire MCP
mcp = get_mcp_manager()

# Statistiques globales
stats = mcp.get_global_stats()
print(f"Total chercheurs: {stats['total_chercheurs']}")
print(f"Total publications: {stats['total_publications']}")

# Top 10 chercheurs
top_chercheurs = mcp.get_top_chercheurs(limit=10)
for chercheur in top_chercheurs:
    print(f"{chercheur['nom']}: {chercheur['nb_publications']} publications")

# Top collaborations
collabs = mcp.get_top_collaborations(limit=5)

# Stats pour un pays spécifique
stats_france = mcp.get_stats_pays(pays="France")

# Trouver des collaborateurs potentiels
collaborateurs = mcp.find_potential_collaborators(nom="John Doe", limit=10)

# Réseau de collaboration
network = mcp.get_collaboration_network(nom="John Doe")
```

### 3. **Appel Dynamique par Nom d'Outil**

```python
from mcp_server.mcp_service import get_mcp_manager

mcp = get_mcp_manager()

# Obtenir la liste des outils disponibles
tools = mcp.list_tools()
for tool in tools:
    print(f"- {tool['name']}: {tool['description']}")

# Exécuter un outil par son nom
result = mcp.execute_tool("get_global_stats")
result = mcp.execute_tool("get_top_chercheurs", limit=5)
result = mcp.execute_tool("get_stats_pays", pays="Canada")
```

## 📋 Outils MCP disponibles

### `get_global_stats()`
**Description**: Statistiques globales de la base de données  
**Paramètres**: Aucun  
**Retour**:
```python
{
    "total_chercheurs": 150,
    "total_publications": 2500,
    "total_institutions": 45,
    "total_collaborations": 300,
    "nb_pays": 25
}
```

### `get_top_chercheurs(limit=10)`
**Description**: Classement des chercheurs par nombre de publications  
**Paramètres**: 
- `limit` (int, optionnel): Nombre de résultats (défaut: 10)

**Retour**:
```python
[
    {
        "nom": "Dr. Smith",
        "nb_publications": 45,
        "total_citations": 1250
    },
    ...
]
```

### `get_top_collaborations(limit=10)`
**Description**: Collaborations les plus fortes  
**Paramètres**:
- `limit` (int, optionnel): Nombre de résultats (défaut: 10)

**Retour**:
```python
[
    {
        "chercheur1": "Dr. Smith",
        "chercheur2": "Dr. Jones",
        "poids": 15
    },
    ...
]
```

### `get_stats_pays(pays=None)`
**Description**: Statistiques de publications par pays  
**Paramètres**:
- `pays` (str, optionnel): Nom du pays (si vide, retourne tous les pays)

**Retour**:
```python
# Avec pays spécifique:
[
    {
        "pays": "France",
        "annee": 2023,
        "nombre_publications": 120
    },
    ...
]

# Sans pays (top 20):
[
    {
        "pays": "USA",
        "total_publications": 5000
    },
    ...
]
```

### `find_potential_collaborators(nom, limit=10)`
**Description**: Suggérer des collaborateurs potentiels pour un chercheur  
**Paramètres**:
- `nom` (str, requis): Nom du chercheur
- `limit` (int, optionnel): Nombre de suggestions (défaut: 10)

**Retour**:
```python
{
    "chercheur_source": "Dr. Smith",
    "suggestions": [
        {
            "nom": "Dr. Johnson",
            "score_compatibilite": 85,
            "raisons": [
                "3 collaborateur(s) en commun : Dr. A, Dr. B, Dr. C",
                "5 thème(s) commun(s) : machine, learning, neural, deep, network",
                "même institution"
            ],
            "nb_publications": 30,
            "nb_collaborateurs": 12
        },
        ...
    ]
}
```

### `get_collaboration_network(nom)`
**Description**: Réseau de collaboration centré sur un chercheur  
**Paramètres**:
- `nom` (str, requis): Nom du chercheur

**Retour**:
```python
{
    "chercheur_central": "Dr. Smith",
    "collaborateurs_directs": [
        {
            "nom": "Dr. Jones",
            "poids": 12,
            "role": "collaborateur principal"
        },
        ...
    ],
    "ponts_vers_clusters": [
        {
            "nom": "Dr. Bridge",
            "role": "pont vers autre cluster",
            "connexions_externes": ["Dr. X", "Dr. Y"]
        }
    ],
    "chercheurs_isoles": ["Dr. Isolated"],
    "statistiques": {
        "nb_collaborateurs": 15,
        "nb_ponts": 3,
        "nb_isoles": 1,
        "densite_reseau": 0.65
    },
    "resume": "Dr. Smith collabore avec 15 chercheurs..."
}
```

## 💡 Exemples d'utilisation dans dash.py

### Exemple 1: Créer un widget de statistiques globales

```python
import streamlit as st
from mcp_server.mcp_service import get_mcp_manager

# Dans votre page dashboard
st.header("📊 Statistiques Globales")

mcp = get_mcp_manager()
stats = mcp.get_global_stats()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Chercheurs", stats['total_chercheurs'])
col2.metric("Publications", stats['total_publications'])
col3.metric("Institutions", stats['total_institutions'])
col4.metric("Collaborations", stats['total_collaborations'])
```

### Exemple 2: Afficher le top des chercheurs

```python
import streamlit as st
import pandas as pd
from mcp_server.mcp_service import get_mcp_manager

st.header("🏆 Top Chercheurs")

mcp = get_mcp_manager()
top_chercheurs = mcp.get_top_chercheurs(limit=10)

# Convertir en DataFrame pour Streamlit
df = pd.DataFrame(top_chercheurs)
st.dataframe(df)

# Ou créer un graphique
import plotly.express as px
fig = px.bar(df, x='nom', y='nb_publications', title='Top 10 Chercheurs')
st.plotly_chart(fig)
```

### Exemple 3: Recherche de collaborateurs avec interface

```python
import streamlit as st
from mcp_server.mcp_service import get_mcp_manager

st.header("🤝 Suggérer des Collaborateurs")

chercheur_name = st.text_input("Nom du chercheur")

if st.button("Rechercher"):
    if chercheur_name:
        mcp = get_mcp_manager()
        result = mcp.find_potential_collaborators(nom=chercheur_name, limit=10)
        
        if "error" in result:
            st.error(result["error"])
        else:
            st.subheader(f"Suggestions pour {result['chercheur_source']}")
            
            for sugg in result['suggestions']:
                with st.expander(f"{sugg['nom']} - Score: {sugg['score_compatibilite']}/100"):
                    st.write(f"**Publications**: {sugg['nb_publications']}")
                    st.write(f"**Collaborateurs**: {sugg['nb_collaborateurs']}")
                    st.write("**Raisons**:")
                    for raison in sugg['raisons']:
                        st.write(f"- {raison}")
    else:
        st.warning("Veuillez entrer un nom de chercheur")
```

### Exemple 4: Visualisation du réseau de collaboration

```python
import streamlit as st
import networkx as nx
import plotly.graph_objects as go
from mcp_server.mcp_service import get_mcp_manager

st.header("🕸️ Réseau de Collaboration")

chercheur_name = st.text_input("Nom du chercheur")

if st.button("Visualiser le réseau"):
    if chercheur_name:
        mcp = get_mcp_manager()
        network = mcp.get_collaboration_network(nom=chercheur_name)
        
        if "error" in network:
            st.error(network["error"])
        else:
            st.write(network['resume'])
            
            # Créer un graphe NetworkX
            G = nx.Graph()
            
            # Ajouter le chercheur central
            G.add_node(network['chercheur_central'], type='central')
            
            # Ajouter les collaborateurs
            for collab in network['collaborateurs_directs']:
                G.add_node(collab['nom'], type='collaborateur')
                G.add_edge(network['chercheur_central'], collab['nom'], weight=collab['poids'])
            
            # Créer la visualisation avec Plotly
            pos = nx.spring_layout(G)
            
            edge_trace = []
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_trace.append(
                    go.Scatter(
                        x=[x0, x1, None],
                        y=[y0, y1, None],
                        mode='lines',
                        line=dict(width=0.5, color='#888'),
                        hoverinfo='none'
                    )
                )
            
            node_trace = go.Scatter(
                x=[pos[node][0] for node in G.nodes()],
                y=[pos[node][1] for node in G.nodes()],
                mode='markers+text',
                text=[node for node in G.nodes()],
                marker=dict(size=10, color='lightblue'),
                textposition="top center"
            )
            
            fig = go.Figure(data=edge_trace + [node_trace])
            fig.update_layout(showlegend=False, hovermode='closest')
            st.plotly_chart(fig)
```

## 🔧 Initialisation

Avant d'utiliser les outils MCP, assurez-vous que:

1. **L'utilisateur est authentifié** (le token API est dans `st.session_state.api_token`)
2. **Les variables d'environnement sont configurées**:
   - `API_BASE_URL`: URL de l'API (défaut: http://api:8000)
   - `GROQ_API_KEY`: Clé API Groq pour le chat LLM

3. **Le gestionnaire MCP est initialisé**:
```python
from mcp_server.mcp_service import get_mcp_manager

# Automatiquement utilise le token de session
mcp = get_mcp_manager()
```

## ⚠️ Gestion des erreurs

Tous les outils peuvent retourner un dictionnaire avec une clé `"error"` en cas d'échec:

```python
from mcp_server.mcp_service import get_mcp_manager

mcp = get_mcp_manager()
result = mcp.find_potential_collaborators(nom="Nom Inexistant")

if isinstance(result, dict) and "error" in result:
    st.error(f"Erreur: {result['error']}")
else:
    # Traiter le résultat
    pass
```

## 📚 Ressources

- **Code serveur MCP**: [mcp_server/researchMCPServer.py](mcp_server/researchMCPServer.py)
- **Service Manager**: [mcp_server/mcp_service.py](mcp_server/mcp_service.py)
- **Client Groq**: [mcp_server/researchClient_groq.py](mcp_server/researchClient_groq.py)
- **Dashboard principal**: [streamlit/dash.py](streamlit/dash.py)
