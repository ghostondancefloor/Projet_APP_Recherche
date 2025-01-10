import json
import streamlit as st
import plotly.express as px

# Charger les données Sankey
sankey_file = "sankey_data.json"
with open(sankey_file, "r", encoding="utf-8") as f:
    sankey_data = json.load(f)

# Compter le nombre d'instituts pour chaque professeur
collab_count = {}

for entry in sankey_data:
    source = entry["source"]
    target = entry["target"]
    
    # Ajouter l'institut à l'ensemble des cibles pour chaque source (prof)
    if source not in collab_count:
        collab_count[source] = set()
    collab_count[source].add(target)

# Convertir les résultats en une liste pour le graphique
data = [{"professor": prof, "num_institutes": len(instituts)} for prof, instituts in collab_count.items()]

# Créer un DataFrame
import pandas as pd
df = pd.DataFrame(data)

# Créer un graphique en barres
fig = px.bar(df, x="professor", y="num_institutes", 
             labels={"professor": "Nom du Professeur", "num_institutes": "Nombre d'Instituts"},
             title="Nombre d'Instituts Collaborés par Chercheur")

# Personnaliser le graphique
fig.update_layout(
    xaxis_title="Chercheur",
    yaxis_title="Nombre d'Instituts",
    font=dict(family="Arial", size=12, color="black"),
)

# Afficher dans Streamlit
st.title("Nombre d'Instituts Collaborés par Chercheur")
st.plotly_chart(fig)
