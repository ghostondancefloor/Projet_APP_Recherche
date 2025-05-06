import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import mysql.connector
from mysql.connector import Error
import os 


def get_top_universities(chercheur_nom, start_year, end_year):
    """
    Récupère les données des top universités associées à un chercheur
    """
    if chercheur_nom == "Tous les chercheurs":
        return None
        
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
            
            # Séparation du nom et du prénom
            nom_parts = chercheur_nom.split()
            if len(nom_parts) > 1:
                prenom = nom_parts[0]
                nom = ' '.join(nom_parts[1:])
                chercheur_condition = "c.nom = %s AND c.prenom = %s"
                params = [nom, prenom, start_year, end_year]
            else:
                chercheur_condition = "c.nom = %s OR c.prenom = %s"
                params = [chercheur_nom, chercheur_nom, start_year, end_year]
            
            # Requête simple pour obtenir le top 10 des universités
            query = f"""
            SELECT 
                i.nom AS University,
                COUNT(DISTINCT p.publication_id) AS Count
            FROM chercheurs c
            JOIN publication_auteurs pa ON c.chercheur_id = pa.chercheur_id
            JOIN publications p ON pa.publication_id = p.publication_id
            JOIN publication_institutions pi ON p.publication_id = pi.publication_id
            JOIN institutions i ON pi.institution_id = i.institution_id
            WHERE {chercheur_condition}
            AND YEAR(p.date_publication) BETWEEN %s AND %s
            GROUP BY i.nom
            ORDER BY COUNT(DISTINCT p.publication_id) DESC
            LIMIT 10
            """
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            return pd.DataFrame(results)
            
    except Error as e:
        print(f"Erreur lors de la récupération des universités: {e}")
        return None
    
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
    
    return None

def create_perfected_university_chart(chercheur_nom, start_year, end_year):
    """
    Crée un graphique donut moderne avec un design amélioré
    """
    # Récupérer les données
    df = get_top_universities(chercheur_nom, start_year, end_year)
    
    if df is None or df.empty:
        return None
    
    # Calculer le total des publications et les pourcentages
    total_publications = df['Count'].sum()
    df['Percentage'] = (df['Count'] / total_publications * 100).round(1)
    
    # Trier par nombre de publications décroissant
    df = df.sort_values('Count', ascending=False)
    
    # Définir une palette de couleurs moderne et professionnelle
    colors = [
        '#3366CC', '#DC3912', '#FF9900', '#109618', '#990099', 
        '#0099C6', '#DD4477', '#66AA00', '#B82E2E', '#316395'
    ]
    
    # Créer un graphique donut plus moderne et élégant
    fig = go.Figure()
    
    fig.add_trace(go.Pie(
        labels=df['University'],
        values=df['Count'],
        textinfo='percent',
        hoverinfo='label+percent+value',
        hovertemplate='<b>%{label}</b><br>Publications: %{value}<br>Pourcentage: %{percent}<extra></extra>',
        marker=dict(
            colors=colors,
            line=dict(color='#FFFFFF', width=2)  # Bordure blanche pour un look plus net
        ),
        showlegend=True,
        hole=0.4,  # Créer un donut au lieu d'un pie
        rotation=90,  # Rotation pour un meilleur alignement avec la légende
        pull=[0.05 if i == 0 else 0 for i in range(len(df))]  # Légèrement tirer le premier segment
    ))
    
    # Ajouter un texte au centre du donut
    fig.add_annotation(
        x=0.5, y=0.5,
        text=f"{total_publications}",
        showarrow=False,
        font=dict(size=24, color='black', family='Arial Black')
    )
    
    fig.add_annotation(
        x=0.5, y=0.46,
        text="publications",
        showarrow=False,
        font=dict(size=14, color='gray', family='Arial')
    )
    
    # Mise en page améliorée
    fig.update_layout(
        legend=dict(
            title=dict(
                text="<b>Universités</b>",
                font=dict(size=14, family="Arial")
            ),
            font=dict(size=12, family="Arial"),
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor="#DDDDDD",
            borderwidth=1,
            x=1.05,
            y=0.5,
            xanchor="left",
            yanchor="middle"
        ),
        height=650,
        width=950,
        margin=dict(l=20, r=180, t=100, b=20),
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    
    return fig

