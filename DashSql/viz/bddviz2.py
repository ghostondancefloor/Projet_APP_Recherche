import plotly.express as px
import pandas as pd
import mysql.connector
from mysql.connector import Error
import os

def get_top5_countries_data(year):
    """
    Récupère les données des top 5 pays collaborateurs pour une année spécifique
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
            
            # Requête SQL pour obtenir le nombre de publications par pays
            query = """
            SELECT 
                p.nom_pays AS country, 
                COUNT(DISTINCT pp.publication_id) AS count
            FROM pays p
            JOIN publication_pays pp ON p.code_pays = pp.code_pays
            JOIN publications pub ON pp.publication_id = pub.publication_id
            WHERE YEAR(pub.date_publication) = %s
            AND p.nom_pays != 'France'
            GROUP BY p.nom_pays
            ORDER BY count DESC
            LIMIT 5
            """
            
            cursor.execute(query, (year,))
            results = cursor.fetchall()
            df = pd.DataFrame(results)
            
            cursor.close()
            connection.close()
            
            return df
            
    except Error as e:
        print(f"Erreur lors de la connexion à MySQL: {e}")
        return pd.DataFrame(columns=['country', 'count'])
    
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
    
    return pd.DataFrame(columns=['country', 'count'])

def create_top5_countries_chart(year):
    """
    Crée un graphique amélioré et simplifié du top 5 des pays collaborateurs
    """
    # Récupérer les données
    df = get_top5_countries_data(year)
    
    if df.empty:
        return None
    
    # Créer un graphique à barres avec Plotly Express
    fig = px.bar(
        df,
        x="country",
        y="count",
        color="count",
        color_continuous_scale="Blues",
        title=f"Top 5 des pays collaborateurs en {year}",
        labels={"country": "Pays", "count": "Nombre de publications"},
        text="count"
    )
    
    # Améliorer la mise en page
    fig.update_traces(
        textposition='outside',
        textfont_size=14,
        marker_line_width=1.5,
        marker_line_color='rgba(0,0,0,0.5)',
        hovertemplate='<b>%{x}</b><br>Publications: %{y}<extra></extra>'
    )
    
    # Configuration globale
    fig.update_layout(
        xaxis_title="Pays",
        yaxis_title="Nombre de publications",
        font_family="Arial",
        title_font_size=20,
        title_x=0.5,
        height=500,
        width=800,
        coloraxis_showscale=False,
        plot_bgcolor='white',
        yaxis=dict(
            gridcolor='lightgray',
            zeroline=True,
            zerolinecolor='lightgray',
            zerolinewidth=1
        ),
        xaxis=dict(
            tickangle=-45 if len(df) > 3 else 0  # Incliner les étiquettes si nécessaire
        )
    )
    
    # Ajouter une annotation avec le total
    total_publications = df['count'].sum()
    fig.add_annotation(
        x=0.5,
        y=1.1,
        xref="paper",
        yref="paper",
        text=f"Total: {total_publications} publications",
        showarrow=False,
        font=dict(size=16),
        bgcolor="rgba(255, 255, 255, 0.8)",
        borderpad=4
    )
    
    return fig

