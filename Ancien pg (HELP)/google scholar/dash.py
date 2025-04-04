import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Charger les données
df = pd.read_csv("data.csv")

# Grouper par chercheur et trier par citations pour chaque chercheur
top_articles_per_researcher = df.groupby(['researcher', 'title'])['value of cited by'].sum().reset_index()

# Trier chaque chercheur par nombre de citations de manière décroissante
top_articles_per_researcher = top_articles_per_researcher.sort_values(by=['researcher', 'value of cited by'], ascending=[True, False])

# Prendre les 5 premiers articles pour chaque chercheur
top_5_articles = top_articles_per_researcher.groupby('researcher').head(5)

# Calculer le nombre total de citations par chercheur
total_citations_per_researcher = df.groupby('researcher')['value of cited by'].sum().reset_index()

# Trier les chercheurs par nombre de citations de manière décroissante
total_citations_per_researcher = total_citations_per_researcher.sort_values(by='value of cited by', ascending=False)

# Prendre les 3 premiers chercheurs pour le podium
top_3_researchers = total_citations_per_researcher.head(3)

# Créer une figure vide pour le graphique Plotly
fig = go.Figure()

# Ajouter une trace pour chaque chercheur
researchers = top_5_articles['researcher'].unique()

# Sidebar filter: sélection des chercheurs
selected_researcher = st.sidebar.selectbox(
    'Select Researcher',
    list(researchers)
)

# Filtrer les données en fonction du chercheur sélectionné
filtered_data = top_5_articles[top_5_articles['researcher'] == selected_researcher]

# Ajouter une trace pour chaque chercheur
for researcher in researchers:
    researcher_data = filtered_data[filtered_data['researcher'] == researcher]
    
    # Trier les articles par ordre décroissant de citations
    researcher_data_sorted = researcher_data.sort_values(by='value of cited by', ascending=False)

    # Ajouter une trace de type "bar"
    fig.add_trace(go.Bar(
        x=researcher_data_sorted['value of cited by'],
        y=researcher_data_sorted['title'],
        name=researcher, 
        orientation='h',
    ))

# Mettre à jour le layout du graphique Plotly
fig.update_layout(
    title="Top 5 Articles Most Cited per Researcher",
    xaxis=dict(title="Number of Citations"),
    yaxis=dict(title="Article Title", autorange="reversed"),  
    barmode='group'
)

# Utiliser `st.columns()` pour diviser la page en deux colonnes
col1, col2 = st.columns([2, 1])

# Afficher le graphique Plotly dans la première colonne
with col1:
    st.plotly_chart(fig)

# Graphique pour le podium des 3 chercheurs dans la deuxième colonne
podium_fig = go.Figure()

# Ajouter une trace de type "bar" pour le podium
podium_fig.add_trace(go.Bar(
    x=top_3_researchers['value of cited by'],
    y=top_3_researchers['researcher'],
    orientation='h',
    marker=dict(color=['gold', 'silver', 'brown']),
))

# Mettre à jour le layout du graphique du podium
podium_fig.update_layout(
    title="Top 3 Researchers by Citations",
    xaxis=dict(title="Total Citations"),
    yaxis=dict(title="Researcher", autorange="reversed"),
)

# Afficher le graphique du podium dans la deuxième colonne
with col2:
    st.plotly_chart(podium_fig)
