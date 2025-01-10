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

# Ajouter une option "Général" au dropdown
chercheurs.insert(0, "Général")

# Générateur de couleurs aléatoires pour chaque chercheur
def generate_chercheur_colors(chercheurs):
    random.seed(42)  # Pour des couleurs constantes entre les exécutions
    return {chercheur: f"rgba({random.randint(0,255)}, {random.randint(0,255)}, {random.randint(0,255)}, 0.8)" for chercheur in chercheurs}

# Générer les couleurs pour chaque chercheur
chercheur_colors = generate_chercheur_colors(chercheurs)

# Fonction pour générer un diagramme de Sankey
def generate_sankey(chercheur_name="Général"):
    sources = []
    targets = []
    values = []
    labels = []
    label_map = {}
    current_index = 0

    # Parcours des collaborations
    for entry in sankey_data:
        if chercheur_name == "Général" or entry["source"] == chercheur_name:
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

    # Générer les couleurs des nœuds et des liens
    node_colors = [chercheur_colors.get(label, "rgba(200, 200, 200, 0.8)") for label in labels]
    link_colors = []

    if chercheur_name == "Général":
        # Chaque flux sortant utilise la couleur du chercheur source
        for source_idx, target_idx in zip(sources, targets):
            link_colors.append(node_colors[source_idx])
    else:
        # Pour un chercheur spécifique, les flux ont des couleurs différentes par institution
        color_map = generate_chercheur_colors(labels)  # Génère des couleurs pour chaque institution
        link_colors = [color_map[labels[target]] for target in targets]

    # Création du Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,  # Espacement vertical accru entre les nœuds
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color=node_colors,
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=link_colors,
            label=[
                f"{labels[s]} → {labels[t]} : {v}" for s, t, v in zip(sources, targets, values)
            ]  # Labels clairs pour les flux
        )
    )])

    # Définir une hauteur fixe de 500 pour tous les diagrammes
    fig.update_layout(
        title_text=f"Diagramme de Sankey pour {'toutes les collaborations' if chercheur_name == 'Général' else chercheur_name}",
        font_size=10,
        height=500
    )
    return fig

# Interface utilisateur avec Streamlit
st.title("Diagramme de Sankey des Collaborations")

# Sélection de l'option (Général ou chercheur spécifique)
selected_chercheur = st.selectbox(
    "Sélectionnez une option :",
    options=chercheurs,
    index=0  # Valeur par défaut : Général
)

# Génération du diagramme de Sankey
fig = generate_sankey(selected_chercheur)

# Affichage du diagramme
st.plotly_chart(fig, use_container_width=True)
