import plotly.graph_objects as go
import mysql.connector
from mysql.connector import Error
import pandas as pd
import os 


def lire_chercheurs_autorises(fichier):
    """
    Lit la liste des chercheurs autorisés à partir d'un fichier
    """
    try:
        with open(fichier, "r", encoding="utf-8") as f:
            chercheurs = [ligne.strip() for ligne in f if ligne.strip()]
        return chercheurs
    except FileNotFoundError:
        print(f"Fichier non trouvé : {fichier}")
        return []

def get_top_articles_by_researcher(researcher_name=None, limit=5):
    """
    Récupère les articles les plus cités pour un chercheur donné
    """
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
            
            # Base de la requête
            query = """
            SELECT 
                CONCAT(c.prenom, ' ', c.nom) AS researcher,
                p.titre AS title,
                p.citations AS cited_by,
                YEAR(p.date_publication) AS year,
                GROUP_CONCAT(DISTINCT CONCAT(c2.prenom, ' ', c2.nom) SEPARATOR '|') AS co_authors,
                GROUP_CONCAT(DISTINCT i.nom SEPARATOR '|') AS institutions
            FROM chercheurs c
            JOIN publication_auteurs pa ON c.chercheur_id = pa.chercheur_id
            JOIN publications p ON pa.publication_id = p.publication_id
            LEFT JOIN publication_auteurs pa2 ON p.publication_id = pa2.publication_id AND pa2.chercheur_id != c.chercheur_id
            LEFT JOIN chercheurs c2 ON pa2.chercheur_id = c2.chercheur_id
            LEFT JOIN publication_institutions pi ON p.publication_id = pi.publication_id
            LEFT JOIN institutions i ON pi.institution_id = i.institution_id
            """
            
            params = []
            
            # Ajouter un filtrage par chercheur si spécifié
            if researcher_name and researcher_name != "Tous les chercheurs":
                # Séparation du nom et du prénom
                nom_parts = researcher_name.split()
                if len(nom_parts) > 1:
                    prenom = nom_parts[0]
                    nom = ' '.join(nom_parts[1:])
                    query += " WHERE c.nom = %s AND c.prenom = %s"
                    params.extend([nom, prenom])
                else:
                    query += " WHERE c.nom = %s OR c.prenom = %s"
                    params.extend([researcher_name, researcher_name])
            
            # Regrouper et trier
            query += " GROUP BY c.chercheur_id, p.publication_id ORDER BY p.citations DESC"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # Traitement post-requête : limiter aux 5 articles les plus cités par chercheur
            if results:
                df = pd.DataFrame(results)
                
                # Traiter les co-auteurs et institutions
                df['co_authors'] = df['co_authors'].apply(
                    lambda x: ', '.join(x.split('|')[:3]) + '...' if x and len(x.split('|')) > 3 else 
                    (', '.join(x.split('|')) if x else 'Aucun')
                )
                
                df['institutions'] = df['institutions'].apply(
                    lambda x: ', '.join(x.split('|')[:2]) + '...' if x and len(x.split('|')) > 2 else 
                    (', '.join(x.split('|')) if x else 'Aucune')
                )
                
                # Tronquer les titres trop longs
                df['short_title'] = df['title'].apply(
                    lambda x: x[:50] + '...' if len(x) > 50 else x
                )
                
                # Obtenir le top 5 des articles par chercheur
                top_articles = df.groupby('researcher').apply(
                    lambda x: x.nlargest(limit, 'cited_by')
                ).reset_index(drop=True)
                
                cursor.close()
                connection.close()
                
                return top_articles
            
            cursor.close()
            connection.close()
            
            return pd.DataFrame()
            
    except Error as e:
        print(f"Erreur lors de la connexion à MySQL: {e}")
        return pd.DataFrame()
    
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
    
    return pd.DataFrame()

def create_improved_top_articles_chart(researcher_name=None):
    """
    Crée un graphique amélioré des articles les plus cités par chercheur
    """
    # Si aucun chercheur n'est spécifié, utiliser les chercheurs autorisés
    if researcher_name is None or researcher_name == "Tous les chercheurs":
        chercheurs_autorises = lire_chercheurs_autorises("researchers.txt")
        if chercheurs_autorises:
            # Limiter à 3 chercheurs pour la lisibilité
            filtered_researchers = chercheurs_autorises[:3]
        else:
            return None
    else:
        filtered_researchers = [researcher_name]
    
    # Récupérer les données
    df = get_top_articles_by_researcher(researcher_name)
    
    if df.empty:
        return None
    
    # Créer un graphique à barres horizontal avec des couleurs par chercheur
    fig = go.Figure()
    
    # Couleurs pour différencier les chercheurs
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    
    # Obtenir la liste des chercheurs uniques
    researchers = df['researcher'].unique()
    
    # Ajouter les barres pour chaque chercheur
    for i, researcher in enumerate(researchers):
        researcher_data = df[df['researcher'] == researcher]
        
        fig.add_trace(go.Bar(
            y=researcher_data['short_title'],
            x=researcher_data['cited_by'],
            orientation='h',
            name=researcher,
            marker=dict(
                color=colors[i % len(colors)],
                line=dict(color='rgba(0,0,0,0.4)', width=1)
            ),
            text=researcher_data['cited_by'],
            textposition='outside',
            customdata=researcher_data[['year', 'co_authors', 'institutions']].values,
            hovertemplate=(
                "<b>%{y}</b><br>" +
                "Citations: %{x}<br>" +
                "Année: %{customdata[0]}<br>" +
                "Co-auteurs: %{customdata[1]}<br>" +
                "Institutions: %{customdata[2]}" +
                "<extra></extra>"
            )
        ))
    
    # Mise en page du graphique
    fig.update_layout(
        # title=dict(
        #     text="<b>Top 5 des articles les plus cités par chercheur</b>",
        #     font=dict(size=20, color="#333333"),
        #     x=0.5
        # ),
        xaxis=dict(
            title=dict(
                text="Nombre de citations",
                font=dict(size=14)
            ),
            gridcolor='lightgray'
        ),
        yaxis=dict(
            title=dict(
                text="Article",
                font=dict(size=14)
            ),
            autorange="reversed"  # Pour afficher le plus cité en haut
        ),
        barmode='group',
        height=700,
        width=1000,
        margin=dict(l=50, r=50, t=80, b=50),
        plot_bgcolor='white',
        legend=dict(
            title=dict(
                text="Chercheur",
                font=dict(size=12)
            ),
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='lightgray',
            borderwidth=1
        ),
        annotations=[
            dict(
                xref="paper",
                yref="paper",
                x=1,
                y=-0.2,
                text=f"Nombre total d'articles: {len(df)} | Chercheurs: {len(researchers)} | Citations totales: {df['cited_by'].sum()}",
                showarrow=False,
                font=dict(size=12, color="#555555"),
                align="right",
                bgcolor="rgba(240,240,240,0.8)",
                borderpad=4,
                bordercolor="lightgray",
                borderwidth=1
            )
        ]
    )
    
    # Si un seul chercheur est sélectionné, ajuster le titre
    if len(researchers) == 1:
        fig.update_layout(
            # title=dict(
            #     text=f"<b>Top 5 des articles les plus cités de {researchers[0]}</b>",
            #     font=dict(size=20, color="#333333"),
            #     x=0.5
            # )
        )
    
    return fig

