import json
import streamlit as st
import plotly.graph_objects as go
import random

# Chargement des données Sankey
sankey_file = "sankey_data.json"
with open(sankey_file, "r", encoding="utf-8") as f:
    sankey_data = json.load(f)

# Liste des chercheurs uniques
chercheurs = list(set(entry["source"] for entry in sankey_data))

# Générateur de couleurs aléatoires pour chaque université
def generate_colors(labels):
    random.seed(42)  # Pour des couleurs constantes entre les exécutions
    return {label: f"rgba({random.randint(0,255)}, {random.randint(0,255)}, {random.randint(0,255)}, 0.8)" for label in labels}

# Fonction pour générer un diagramme de Sankey pour un chercheur
def generate_sankey(chercheur_name):
    sources = []
    targets = []
    values = []
    labels = []
    label_map = {}
    current_index = 0

    # Parcours des collaborations
    for entry in sankey_data:
        if entry["source"] == chercheur_name:
            source = entry["source"]
            target = entry["target"]
            value = entry["value"]

            # Ajouter source au mapping
            if source not in label_map:
                label_map[source] = current_index
                labels.append(source)
                current_index += 1

            # Ajouter target au mapping
            if target not in label_map:
                label_map[target] = current_index
                labels.append(target)
                current_index += 1

            # Ajouter les données au graphique
            sources.append(label_map[source])
            targets.append(label_map[target])
            values.append(value)

    # Générer les couleurs basées sur les labels des universités
    color_map = generate_colors(labels)
    colors = [color_map[labels[target]] for target in targets]

    # Création du Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,  # Espacement vertical accru entre les nœuds
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color=[color_map[label] for label in labels],
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=colors,
            label=[f"{labels[s]} → {labels[t]} : {v}" for s, t, v in zip(sources, targets, values)]
        )
    )])

    # Personnalisation de la police des labels des nœuds dans le layout global
    fig.update_layout(
        title_text=f"Diagramme de Sankey pour {chercheur_name}",
        font=dict(
            size=12,  # Taille de la police du titre et des labels
            color="black",  # Couleur noire du texte
            family="Arial"  # Police standard
        ),
        height=700,  # Augmenter la hauteur du graphique pour plus d'espace
        width=1000,  # Augmenter la largeur du graphique pour le rendre plus grand
        margin=dict(l=0, r=0, t=40, b=40)  # Ajuster les marges autour du graphique
    )
    return fig

# Création de l'application Streamlit
st.title("Diagramme de Sankey des Collaborations")

# Sélection du chercheur
selected_chercheur = st.selectbox("Sélectionnez un chercheur :", chercheurs)

# Générer et afficher le Sankey
fig = generate_sankey(selected_chercheur)
st.plotly_chart(fig, use_container_width=True)
