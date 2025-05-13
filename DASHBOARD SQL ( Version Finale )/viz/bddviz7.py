import plotly.express as px
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

def get_institute_count_per_researcher(professor_list=None):
    """
    Récupère le nombre d'institutions distinctes avec lesquelles chaque chercheur a collaboré
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
            
            # Requête SQL simplifiée
            query = """
            SELECT 
                CONCAT(c.prenom, ' ', c.nom) AS professor,
                COUNT(DISTINCT i.institution_id) AS num_institutes
            FROM chercheurs c
            JOIN publication_auteurs pa ON c.chercheur_id = pa.chercheur_id
            JOIN publications p ON pa.publication_id = p.publication_id
            JOIN publication_institutions pi ON p.publication_id = pi.publication_id
            JOIN institutions i ON pi.institution_id = i.institution_id
            """
            
            params = []
            
            # Ajouter le filtrage par liste de professeurs si fournie
            if professor_list and len(professor_list) > 0 and "Tous les chercheurs" not in professor_list:
                placeholders = ', '.join(['%s'] * len(professor_list))
                query += f" WHERE CONCAT(c.prenom, ' ', c.nom) IN ({placeholders})"
                params.extend(professor_list)
            
            query += " GROUP BY c.chercheur_id ORDER BY COUNT(DISTINCT i.institution_id) DESC"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            return results
            
    except Error as e:
        print(f"Erreur lors de la connexion à MySQL: {e}")
        return []
    
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
    
    return []

def create_simple_institutions_chart():
    """
    Crée un graphique simple et clair du nombre d'institutions par chercheur
    """
    # Lire la liste des chercheurs autorisés
    chercheurs_autorises = lire_chercheurs_autorises("researchers.txt")
    
    # Récupérer les données
    collab_data = get_institute_count_per_researcher(chercheurs_autorises)
    
    if not collab_data:
        return None
    
    # Convertir en DataFrame pour manipulation facile
    df = pd.DataFrame(collab_data)
    
    # Limiter à 20 chercheurs pour la lisibilité
    if len(df) > 20:
        df = df.head(20)
    
    # Trier par nombre d'institutions décroissant
    df = df.sort_values('num_institutes', ascending=False)
    
    # Créer un simple graphique à barres vertical avec Plotly Express
    fig = px.bar(
        df,
        x='professor',
        y='num_institutes',
        labels={'professor': 'Chercheur', 'num_institutes': 'Nombre d\'institutions'},
        text='num_institutes',
        color='num_institutes',
        color_continuous_scale='Blues',
        height=600,
        width=1000
    )
    
    # Améliorer la mise en page
    fig.update_traces(
        textposition='outside',
        textfont_size=12,
        marker_line_width=1.5,
        marker_line_color='rgba(0,0,0,0.5)'
    )
    
    fig.update_layout(
        title={
            'text': '<b>Nombre d\'institutions collaborées par chercheur</b>',
            'font': {'size': 20, 'color': '#333333'},
            'x': 0.5,
            'y': 0.95
        },
        xaxis={
            'title': 'Chercheur',
            'tickangle': -45,
            'title_font': {'size': 14}
        },
        yaxis={
            'title': 'Nombre d\'institutions',
            'title_font': {'size': 14},
            'gridcolor': 'lightgray'
        },
        plot_bgcolor='white',
        coloraxis_showscale=False,
        margin={'l': 50, 'r': 50, 't': 80, 'b': 120}
    )
    
    # Ajouter une ligne pour la moyenne
    fig.add_hline(
        y=df['num_institutes'].mean(),
        line_dash="dash",
        line_color="red",
        annotation_text=f"Moyenne: {df['num_institutes'].mean():.1f}",
        annotation_position="top right"
    )
    
    return fig

