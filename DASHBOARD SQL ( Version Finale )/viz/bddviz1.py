import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import mysql.connector
from mysql.connector import Error
import os 

def get_country_collaboration_data(year):
    """
    Récupère les données de collaboration par pays pour une année spécifique
    """
    try:
        # Configurer la connexion à la base de données

        connection = mysql.connector.connect(
        host=os.getenv("DB_HOST", "db"),
        user=os.getenv("DB_USER", "user"),
        password=os.getenv("DB_PASS", "userpass"),
        database=os.getenv("DB_NAME", "dashboarddb"),
        port=int(os.getenv("DB_PORT", "3306"))
)

        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            # Requête SQL améliorée pour obtenir plus d'informations
            query = """
            SELECT 
                p.nom_pays AS country, 
                p.code_pays AS country_code,
                COUNT(DISTINCT pp.publication_id) AS count,
                YEAR(pub.date_publication) AS year,
                COUNT(DISTINCT c.chercheur_id) AS num_researchers,
                GROUP_CONCAT(DISTINCT c.prenom, ' ', c.nom SEPARATOR ', ') AS researchers
            FROM pays p
            JOIN publication_pays pp ON p.code_pays = pp.code_pays
            JOIN publications pub ON pp.publication_id = pub.publication_id
            JOIN publication_auteurs pa ON pub.publication_id = pa.publication_id
            JOIN chercheurs c ON pa.chercheur_id = c.chercheur_id
            WHERE YEAR(pub.date_publication) = %s
            GROUP BY p.nom_pays, p.code_pays, YEAR(pub.date_publication)
            ORDER BY count DESC
            """
            
            cursor.execute(query, (year,))
            results = cursor.fetchall()
            df = pd.DataFrame(results)
            
            if df.empty:
                df = pd.DataFrame([{
                    'country': 'France', 
                    'country_code': 'FR',
                    'count': 0, 
                    'year': year,
                    'num_researchers': 0,
                    'researchers': ''
                }])
            else:
                # Limiter la liste des chercheurs pour éviter des textes trop longs
                df['researchers'] = df['researchers'].apply(
                    lambda x: ', '.join(x.split(', ')[:5]) + '...' if len(x.split(', ')) > 5 else x
                )
                
                # Assurer que la France est présente
                if 'France' not in df['country'].values:
                    df = pd.concat([
                        df, 
                        pd.DataFrame([{
                            'country': 'France', 
                            'country_code': 'FR',
                            'count': 0, 
                            'year': year,
                            'num_researchers': 0,
                            'researchers': ''
                        }])
                    ], ignore_index=True)
                else:
                    # Mettre en évidence la France différemment sans modifier sa valeur
                    df.loc[df['country'] == 'France', 'country_code'] = 'FR_HIGHLIGHT'
            
            df['year'] = df['year'].astype(str)
            cursor.close()
            connection.close()
            
            return df
            
    except Error as e:
        print(f"Erreur lors de la connexion à MySQL: {e}")
        return pd.DataFrame(columns=['country', 'country_code', 'count', 'year', 'num_researchers', 'researchers'])
    
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
    
    return pd.DataFrame(columns=['country', 'country_code', 'count', 'year', 'num_researchers', 'researchers'])

def create_enhanced_map(year):
    """
    Crée une carte du monde améliorée montrant les collaborations par pays
    """
    # Récupérer les données
    df = get_country_collaboration_data(year)
    
    if df.empty:
        return None
    
    # Séparer la France pour un traitement spécial
    df_france = df[df['country'] == 'France'].copy()
    df_other = df[df['country'] != 'France'].copy()
    
    # Créer les textes d'info-bulle personnalisés
    df_other['hover_text'] = df_other.apply(
        lambda row: f"<b>{row['country']}</b><br>" +
                   f"Publications: {row['count']}<br>" +
                   f"Chercheurs: {row['num_researchers']}<br>" +
                   f"Collaborateurs: {row['researchers']}",
        axis=1
    )
    
    # Créer la carte de base avec choropleth
    fig = px.choropleth(
        df_other,
        locations="country",
        locationmode="country names",
        color="count",
        hover_name="country",
        custom_data=["hover_text"],
        # title=f"Carte des pays collaborateurs en {year}",
        color_continuous_scale="Plasma",
        range_color=[0, df_other['count'].max()],
        labels={"count": "Nombre de publications"},
        projection="natural earth"
    )
    
    # Personnaliser l'info-bulle
    fig.update_traces(
        hovertemplate="%{customdata[0]}<extra></extra>"
    )
    
    # Ajouter un marqueur pour la France
    fig.add_scattergeo(
        locations=["France"],
        locationmode="country names",
        marker=dict(
            size=15,
            color="black",
            symbol="star",
            line=dict(width=2, color="white")
        ),
        name="France",
        text="France",
        hoverinfo="text",
        hovertext="<b>France</b><br>(Pays de référence)"
    )
    
    # Améliorer la mise en page de la carte
    fig.update_geos(
        showcoastlines=True,
        coastlinecolor="RebeccaPurple",
        showland=True,
        landcolor="rgb(243, 243, 243)",
        showocean=True,
        oceancolor="lightblue",
        showlakes=True,
        lakecolor="lightblue",
        showrivers=True,
        rivercolor="lightblue",
        showcountries=True,
        countrycolor="gray",
        showframe=False,
        resolution=110
    )
    
    # Mise en page générale
    fig.update_layout(
        # title=dict(
        #     text=f"<b>Collaborations internationales en {year}</b>",
        #     font=dict(size=24, color="RebeccaPurple"),
        #     x=0.5,
        #     xanchor="center"
        # ),
        coloraxis_colorbar=dict(
            title="Nombre de publications",
            tickformat="d",
            outlinecolor="black",
            outlinewidth=1,
            len=0.7,
            thickness=20,
            yanchor="middle"
        ),
        height=700,
        width=1200,
        margin=dict(l=0, r=0, t=60, b=0),
        paper_bgcolor="white",
        geo=dict(
            bgcolor="white",
            showsubunits=True,
            subunitcolor="lightgray"
        ),
        annotations=[
            dict(
                x=0.01,
                y=0.01,
                xref="paper",
                yref="paper",
                text=f"Données de l'année {year} | France marquée par ★",
                showarrow=False,
                font=dict(size=12, color="gray")
            )
        ]
    )
    
    # Ajouter un texte explicatif sur la carte
    fig.add_annotation(
        x=0.01,
        y=0.98,
        xref="paper",
        yref="paper",
        text=f"Total de {df_other['count'].sum()} publications avec {len(df_other)} pays",
        showarrow=False,
        font=dict(size=14, color="black"),
        bgcolor="rgba(255, 255, 255, 0.8)",
        bordercolor="gray",
        borderwidth=1,
        borderpad=4,
        align="left"
    )
    
    return fig

