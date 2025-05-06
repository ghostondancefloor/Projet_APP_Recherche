import plotly.graph_objects as go
import pandas as pd
import mysql.connector
from mysql.connector import Error
import random
import colorsys

def generate_harmonic_colors(n_colors, saturation=0.7, value=0.9):
    """
    Génère une palette de couleurs harmonieuses basée sur la roue chromatique
    """
    colors = []
    for i in range(n_colors):
        # Utiliser le nombre d'or pour répartir les couleurs harmonieusement
        hue = (i * 0.618033988749895) % 1.0
        # Convertir HSV en RGB puis en hex
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        color = f"rgba({int(r*255)}, {int(g*255)}, {int(b*255)}, 0.8)"
        colors.append(color)
    return colors

def get_sankey_data(chercheur_nom):
    """
    Récupère les données pour le diagramme de Sankey
    en établissant la relation entre un chercheur et ses institutions
    """
    if chercheur_nom == "Tous les chercheurs":
        return []
        
    try:
        # Configurer la connexion à la base de données
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="bdd"
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            # Séparation du nom et du prénom
            nom_parts = chercheur_nom.split()
            if len(nom_parts) > 1:
                prenom = nom_parts[0]
                nom = ' '.join(nom_parts[1:])
                chercheur_condition = "c.nom = %s AND c.prenom = %s"
                params = [nom, prenom]
            else:
                chercheur_condition = "c.nom = %s OR c.prenom = %s"
                params = [chercheur_nom, chercheur_nom]
            
            # Requête principale
            query = f"""
            SELECT 
                CONCAT(c.prenom, ' ', c.nom) AS source,
                i.nom AS target,
                COUNT(DISTINCT pa.publication_id) AS value,
                MIN(YEAR(p.date_publication)) AS first_year,
                MAX(YEAR(p.date_publication)) AS last_year,
                IFNULL(SUM(p.citations), 0) AS total_citations
            FROM chercheurs c
            JOIN publication_auteurs pa ON c.chercheur_id = pa.chercheur_id
            JOIN publications p ON pa.publication_id = p.publication_id
            JOIN publication_institutions pi ON p.publication_id = pi.publication_id
            JOIN institutions i ON pi.institution_id = i.institution_id
            WHERE {chercheur_condition}
            GROUP BY c.chercheur_id, i.institution_id
            HAVING COUNT(DISTINCT pa.publication_id) > 0
            ORDER BY COUNT(DISTINCT pa.publication_id) DESC
            """
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # Chercher aussi les publications du chercheur sans institution associée
            query_solo = f"""
            SELECT 
                CONCAT(c.prenom, ' ', c.nom) AS source,
                'Publications sans institution' AS target,
                COUNT(DISTINCT p.publication_id) AS value,
                MIN(YEAR(p.date_publication)) AS first_year,
                MAX(YEAR(p.date_publication)) AS last_year,
                IFNULL(SUM(p.citations), 0) AS total_citations
            FROM chercheurs c
            JOIN publication_auteurs pa ON c.chercheur_id = pa.chercheur_id
            JOIN publications p ON pa.publication_id = p.publication_id
            LEFT JOIN publication_institutions pi ON p.publication_id = pi.publication_id
            WHERE {chercheur_condition} AND pi.institution_id IS NULL
            GROUP BY c.chercheur_id
            HAVING COUNT(DISTINCT p.publication_id) > 0
            """
            
            cursor.execute(query_solo, params)
            solo_results = cursor.fetchall()
            
            # Combiner les résultats
            combined_results = results + solo_results
            
            # S'assurer que toutes les valeurs sont du bon type
            for result in combined_results:
                # Convertir les citations en nombre
                result['total_citations'] = int(result['total_citations']) if result['total_citations'] is not None else 0
                
                # S'assurer que les années sont des entiers ou None
                result['first_year'] = int(result['first_year']) if result['first_year'] is not None else None
                result['last_year'] = int(result['last_year']) if result['last_year'] is not None else None
            
            cursor.close()
            connection.close()
            
            return combined_results
            
    except Error as e:
        print(f"Erreur lors de la connexion à MySQL: {e}")
        return []
    
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
    
    return []

def generate_improved_sankey(chercheur_nom):
    """
    Crée un diagramme de Sankey amélioré qui montre les relations
    entre un chercheur et ses institutions collaboratrices
    """
    # Récupérer les données
    sankey_data = get_sankey_data(chercheur_nom)
    
    if not sankey_data:
        return None
    
    # Préparation des données pour le diagramme
    sources, targets, values, labels = [], [], [], []
    link_colors, link_infos = [], []
    label_map, current_index = {}, 0
    
    # Calculer le total des publications pour le chercheur
    total_pubs = sum(entry["value"] for entry in sankey_data)
    
    # Traitement des données
    for entry in sankey_data:
        source, target, value = entry["source"], entry["target"], entry["value"]
        first_year = entry["first_year"] if entry["first_year"] is not None else "?"
        last_year = entry["last_year"] if entry["last_year"] is not None else "?"
        total_citations = entry["total_citations"] if entry["total_citations"] is not None else 0
        
        # Calcul des métriques
        duration = last_year - first_year + 1 if isinstance(first_year, int) and isinstance(last_year, int) else "?"
        avg_citations = round(total_citations / value, 1) if value > 0 else 0
        percentage = round((value / total_pubs) * 100, 1) if total_pubs > 0 else 0
        
        # Stocker toutes ces informations pour l'infobulle
        link_info = {
            "source": source,
            "target": target,
            "publications": value,
            "first_year": first_year,
            "last_year": last_year,
            "duration": duration,
            "citations": total_citations,
            "avg_citations": avg_citations,
            "percentage": percentage
        }
        link_infos.append(link_info)
        
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
    
    # Générer des couleurs harmonieuses pour les nœuds
    node_colors = generate_harmonic_colors(len(labels))
    
    # Trier les institutions par nombre de publications
    institutions_sorted = sorted(
        [(i, label) for i, label in enumerate(labels) if label != chercheur_nom],
        key=lambda x: -values[sources.index(label_map[chercheur_nom])] if x[1] != chercheur_nom else 0
    )
    
    # Générer une palette de couleurs pour les liens basée sur l'importance
    max_value = max(values)
    link_colors = []
    for i, value in enumerate(values):
        # Couleur basée sur l'importance relative (plus le lien est fort, plus la couleur est intense)
        intensity = 0.3 + 0.7 * (value / max_value)
        
        # Récupérer la couleur du nœud cible
        target_idx = targets[i]
        target_color = node_colors[target_idx]
        
        # Extraire les composantes RGBA
        rgba = target_color.strip('rgba()').split(',')
        r, g, b = int(rgba[0]), int(rgba[1]), int(rgba[2])
        
        # Créer une version plus transparente pour le lien
        link_color = f"rgba({r}, {g}, {b}, {intensity})"
        link_colors.append(link_color)
    
    # Création des infobulles personnalisées pour les liens
    link_hovertexts = []
    for info in link_infos:
        period_text = f"{info['first_year']}-{info['last_year']}"
        duration_text = f"{info['duration']} ans" if isinstance(info['duration'], int) else "Durée inconnue"
        
        hovertext = (
            f"<b>{info['source']} → {info['target']}</b><br>"
            f"Publications: {info['publications']} ({info['percentage']}% du total)<br>"
            f"Période: {period_text} ({duration_text})<br>"
            f"Citations: {info['citations']} (moy. {info['avg_citations']} par publication)"
        )
        link_hovertexts.append(hovertext)
    
    # Créer le diagramme de Sankey
    fig = go.Figure(data=[go.Sankey(
        arrangement="snap",  # Pour un meilleur arrangement des nœuds
        node=dict(
            pad=20,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color=node_colors,
            hovertemplate="%{label}<extra></extra>"
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=link_colors,
            hovertemplate=link_hovertexts,
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                font_family="Arial"
            )
        )
    )])

    # Mise en page améliorée
    fig.update_layout(
        title=dict(
            text=f"<b>Collaborations de {chercheur_nom} avec les institutions</b>",
            font=dict(size=20, color="#2c3e50", family="Arial"),
            x=0.5,
            xanchor="center"
        ),
        font=dict(size=14, color="#34495e", family="Arial"),
        height=700,
        width=1000,
        margin=dict(l=20, r=20, t=60, b=30),
        paper_bgcolor="white",
        plot_bgcolor="white"
    )
    
    # Ajouter une annotation avec un résumé
    source_idx = label_map.get(chercheur_nom, None)
    if source_idx is not None:
        top_institutions = []
        for i, (s, t) in enumerate(zip(sources, targets)):
            if s == source_idx:
                top_institutions.append((t, values[i]))
        
        top_institutions.sort(key=lambda x: -x[1])  # Trier par valeur décroissante
        top_inst_names = [labels[inst_idx] for inst_idx, _ in top_institutions[:3]]
    else:
        top_inst_names = []
    
    top_inst_text = ", ".join(top_inst_names) if top_inst_names else "Aucune"
    
    fig.add_annotation(
        x=0.01,
        y=1,
        xref="paper",
        yref="paper",
        text=(f"<b>Résumé:</b> {total_pubs} publications | "
              f"{len(set(targets))} institutions "),
        showarrow=False,
        font=dict(size=13, color="#34495e"),
        align="left",
        bgcolor="rgba(255, 255, 255, 0.8)",
        bordercolor="#d3d3d3",
        borderwidth=1,
        borderpad=6,
        xanchor="left",
        yanchor="top"
    )
    
    return fig

# Exemple d'utilisation
selected_researcher = "Ilham ALLOUI"  # Remplacer par le nom du chercheur
fig_sankey = generate_improved_sankey(selected_researcher)

if fig_sankey:
    fig_sankey.show()
else:
    print(f"Aucune donnée trouvée pour {selected_researcher}")