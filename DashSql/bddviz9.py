import plotly.graph_objects as go
import mysql.connector
from mysql.connector import Error
import pandas as pd

def get_top_researchers_by_citations(limit=3):
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="bdd"
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            # Requête pour obtenir le total des citations par chercheur
            query = """
            SELECT 
                CONCAT(c.prenom, ' ', c.nom) AS researcher,
                SUM(p.citations) AS value_of_cited_by
            FROM chercheurs c
            JOIN publication_auteurs pa ON c.chercheur_id = pa.chercheur_id
            JOIN publications p ON pa.publication_id = p.publication_id
            GROUP BY c.chercheur_id
            ORDER BY SUM(p.citations) DESC
            LIMIT %s
            """
            
            cursor.execute(query, (limit,))
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

# Récupérer les données
top_3_researchers = get_top_researchers_by_citations(3)

# Créer le graphique si des données sont disponibles
if top_3_researchers:
    df = pd.DataFrame(top_3_researchers)
    
    # Création du graphique en barres (podium)
    podium_fig = go.Figure()
    
    # Ajouter les barres avec des couleurs spécifiques
    podium_fig.add_trace(go.Bar(
        x=df['researcher'],
        y=df['value_of_cited_by'],
        marker=dict(color=['gold', 'silver', 'brown']),  # Couleurs de médaille
        text=df['value_of_cited_by'],
        textposition='auto'
    ))
    
    # Mise en page
    podium_fig.update_layout(
        title="Top 3 Chercheurs par Citations",
        xaxis=dict(title="Chercheur"),
        yaxis=dict(title="Citations Totales"),
        height=600,
        width=800
    )
    
    # Afficher la figure
    podium_fig.show()
else:
    print("Aucune donnée de citations trouvée.")