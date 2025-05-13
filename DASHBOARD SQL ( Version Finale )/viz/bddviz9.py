import plotly.graph_objects as go
import mysql.connector
from mysql.connector import Error
import pandas as pd
import os


def get_top_researchers_by_citations(limit=3):
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "db"),
            user=os.getenv("DB_USER", "user"),
            password=os.getenv("DB_PASS", "userpass"),
            database=os.getenv("DB_NAME", "dashboarddb"),
            port=int(os.getenv("DB_PORT", "3306"))
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
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


def create_top3_researchers_chart():
    top_3_researchers = get_top_researchers_by_citations(3)
    
    if not top_3_researchers:
        return None

    df = pd.DataFrame(top_3_researchers)

    podium_fig = go.Figure()
    podium_fig.add_trace(go.Bar(
        x=df['researcher'],
        y=df['value_of_cited_by'],
        marker=dict(color=['gold', 'silver', 'brown']),
        text=df['value_of_cited_by'],
        textposition='auto'
    ))

    podium_fig.update_layout(
        # title="Top 3 Chercheurs par Citations",
        xaxis=dict(title="Chercheur"),
        yaxis=dict(title="Citations Totales"),
        height=600,
        width=800
    )

    return podium_fig
