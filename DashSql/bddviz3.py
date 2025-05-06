import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import mysql.connector
from mysql.connector import Error
import numpy as np
import colorsys

def get_publications_by_year(start_year, end_year, chercheur_nom=None):
    """
    Récupère les données de publications par année pour une période donnée
    avec option de filtrage par chercheur
    """
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
            
            # Base de la requête SQL
            base_query = """
            SELECT 
                YEAR(pub.date_publication) AS publicationYear, 
                COUNT(DISTINCT pub.publication_id) AS count,
                SUM(pub.citations) AS total_citations,
                COUNT(DISTINCT pi.institution_id) AS unique_institutions
            FROM publications pub
            JOIN publication_auteurs pa ON pub.publication_id = pa.publication_id
            JOIN chercheurs c ON pa.chercheur_id = c.chercheur_id
            LEFT JOIN publication_institutions pi ON pub.publication_id = pi.publication_id
            WHERE YEAR(pub.date_publication) BETWEEN %s AND %s
            """
            
            params = [start_year, end_year]
            
            # Filtrer par chercheur si spécifié
            if chercheur_nom and chercheur_nom != 'Tous les chercheurs':
                # Extraction du nom et prénom à partir du nom complet
                nom_parts = chercheur_nom.split()
                if len(nom_parts) > 1:
                    prenom = nom_parts[0]
                    nom = ' '.join(nom_parts[1:])
                    base_query += " AND c.nom = %s AND c.prenom = %s"
                    params.extend([nom, prenom])
                else:
                    base_query += " AND (c.nom = %s OR c.prenom = %s)"
                    params.extend([chercheur_nom, chercheur_nom])
            
            # Grouper par année et trier
            base_query += " GROUP BY YEAR(pub.date_publication) ORDER BY publicationYear"
            
            cursor.execute(base_query, tuple(params))
            results = cursor.fetchall()
            df = pd.DataFrame(results)
            
            # S'assurer que toutes les années sont incluses, même celles sans publications
            if not df.empty:
                all_years = list(range(start_year, end_year + 1))
                years_df = pd.DataFrame({'publicationYear': all_years})
                df = pd.merge(years_df, df, on='publicationYear', how='left')
                df.fillna({'count': 0, 'total_citations': 0, 'unique_institutions': 0}, inplace=True)
                df['count'] = df['count'].astype(int)
                df['total_citations'] = df['total_citations'].astype(int)
                df['unique_institutions'] = df['unique_institutions'].astype(int)
                
                # Calculer la moyenne mobile sur 3 ans pour montrer la tendance
                df['trend'] = df['count'].rolling(window=3, center=True).mean()
                
                # Calculer les citations moyennes par publication
                df['citations_per_pub'] = np.where(df['count'] > 0, 
                                                  df['total_citations'] / df['count'], 
                                                  0)
            
            cursor.close()
            connection.close()
            
            return df
            
    except Error as e:
        print(f"Erreur lors de la connexion à MySQL: {e}")
        return pd.DataFrame(columns=['publicationYear', 'count', 'total_citations', 'unique_institutions'])
    
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
    
    return pd.DataFrame(columns=['publicationYear', 'count', 'total_citations', 'unique_institutions'])

def create_perfected_publications_chart(start_year, end_year, chercheur_nom=None):
    """
    Crée un graphique perfectionné des publications par année avec une meilleure
    palette de couleurs et plus d'informations contextuelles
    """
    # Récupérer les données
    df = get_publications_by_year(start_year, end_year, chercheur_nom)
    
    if df.empty:
        return None
    
    # Palette de couleurs améliorée - Utilisation d'une palette professionnelle et harmonieuse
    primary_color = '#1f77b4'  # Bleu principal
    secondary_color = '#ff7f0e'  # Orange pour la tendance
    highlight_color = '#2ca02c'  # Vert pour les points importants
    accent_color = '#d62728'  # Rouge pour les annotations
    background_color = '#f8f9fa'  # Gris très clair presque blanc
    grid_color = '#e0e0e0'  # Gris clair pour la grille
    
    # Créer un sous-graphique pour avoir un graphique principal et un petit graphique secondaire
    fig = make_subplots(
        rows=2, cols=1, 
        row_heights=[0.8, 0.2],
        subplot_titles=("", "Citations moyennes par publication"),
        vertical_spacing=0.2
    )
    
    # Créer un dégradé de couleur pour les barres en fonction de l'année
    num_years = len(df)
    color_scale = [primary_color]
    if num_years > 1:
        # Créer un dégradé de couleurs entre primary_color et secondary_color
        h1, s1, v1 = colorsys.rgb_to_hsv(31/255, 119/255, 180/255)  # primary_color en RGB normalisé
        h2, s2, v2 = colorsys.rgb_to_hsv(255/255, 127/255, 14/255)  # secondary_color en RGB normalisé
        
        colors = []
        for i in range(num_years):
            # Interpolation linéaire entre les deux couleurs
            h = h1 + (h2 - h1) * (i / (num_years - 1)) if num_years > 1 else h1
            s = s1 + (s2 - s1) * (i / (num_years - 1)) if num_years > 1 else s1
            v = v1 + (v2 - v1) * (i / (num_years - 1)) if num_years > 1 else v1
            
            # Conversion HSV -> RGB -> Hex
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            color = f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'
            colors.append(color)
        
        color_scale = colors
    
    # Définir les couleurs des barres selon les années
    bar_colors = color_scale if len(color_scale) == num_years else [primary_color] * num_years
    
    # Ajouter les barres pour le nombre de publications (avec dégradé de couleur)
    for i, (year, count) in enumerate(zip(df['publicationYear'], df['count'])):
        fig.add_trace(go.Bar(
            x=[year],
            y=[count],
            name=str(year),
            marker_color=bar_colors[i],
            opacity=0.85,
            hovertemplate='<b>%{x}</b><br>' +
                          'Publications: %{y}<br>' +
                          'Citations: %{customdata[0]}<br>' +
                          'Institutions: %{customdata[1]}<extra></extra>',
            customdata=[[df.loc[df['publicationYear'] == year, 'total_citations'].values[0],
                         df.loc[df['publicationYear'] == year, 'unique_institutions'].values[0]]],
            showlegend=False,
            text=[count] if count > 0 else None,
            textposition='auto',
            textfont=dict(color='white', size=12)
        ), row=1, col=1)
    
    # Ajouter la ligne de tendance si nous avons suffisamment d'années
    if len(df) >= 3:
        fig.add_trace(go.Scatter(
            x=df['publicationYear'],
            y=df['trend'],
            mode='lines',
            line=dict(width=3, color=secondary_color, dash='solid'),
            name='Tendance (moy. mobile 3 ans)',
            hovertemplate='Tendance: %{y:.1f}<extra></extra>'
        ), row=1, col=1)
    
    # Ajouter le graphique de citations moyennes par publication (en bas)
    fig.add_trace(go.Scatter(
        x=df['publicationYear'],
        y=df['citations_per_pub'],
        mode='lines+markers',
        line=dict(width=2, color=highlight_color),
        marker=dict(size=8, color=highlight_color, symbol='diamond'),
        name='Citations par publication',
        hovertemplate='<b>%{x}</b><br>Citations/publication: %{y:.1f}<extra></extra>'
    ), row=2, col=1)
    
    # Calculer la croissance année par année
    if len(df) > 1:
        df['growth'] = df['count'].pct_change() * 100
        
        # Ajouter des annotations de croissance pour les années avec forte variation
        significant_change = df[abs(df['growth']) > 20].copy()  # Filtrer pour des changements significatifs >20%
        
        for _, row in significant_change.iterrows():
            if not np.isnan(row['growth']):
                direction = "▲" if row['growth'] > 0 else "▼"
                color = "#2ecc71" if row['growth'] > 0 else "#e74c3c"  # Vert ou rouge
                
                fig.add_annotation(
                    x=row['publicationYear'],
                    y=row['count'],
                    text=f"{direction} {abs(row['growth']):.0f}%",
                    showarrow=False,
                    font=dict(size=12, color=color, family="Arial Black"),
                    bgcolor="rgba(255, 255, 255, 0.8)",
                    bordercolor=color,
                    borderwidth=1,
                    borderpad=3,
                    yshift=20
                )
    
    # Trouver les années avec le maximum et le minimum de publications
    if not df[df['count'] > 0].empty:
        max_year = df.loc[df['count'].idxmax(), 'publicationYear']
        max_count = df['count'].max()
        min_year_with_pubs = df[df['count'] > 0]['count'].idxmin()
        min_year = df.loc[min_year_with_pubs, 'publicationYear'] if not pd.isna(min_year_with_pubs) else None
        min_count = df.loc[min_year_with_pubs, 'count'] if not pd.isna(min_year_with_pubs) else 0
        
        # Mettre en évidence l'année avec le plus de publications
        if max_count > 0:
            fig.add_trace(go.Scatter(
                x=[max_year],
                y=[max_count],
                mode='markers',
                marker=dict(
                    symbol='star',
                    size=15,
                    color='gold',
                    line=dict(color='black', width=1)
                ),
                name='Maximum',
                hoverinfo='skip',
                showlegend=False
            ), row=1, col=1)
    
    # Titre personnalisé selon la sélection
    
    # Mettre à jour la mise en page
    fig.update_layout(
        xaxis=dict(
            title="Année",
            tickmode='linear',
            dtick=1,  # Afficher chaque année
            gridcolor=grid_color,
            tickfont=dict(size=12)
        ),
        yaxis=dict(
            title="Nombre de publications",
            gridcolor=grid_color,
            zeroline=True,
            zerolinecolor=grid_color,
            zerolinewidth=2,
            tickfont=dict(size=12)
        ),
        xaxis2=dict(
            title="",
            tickmode='linear',
            dtick=1,
            gridcolor=grid_color,
            tickfont=dict(size=10)
        ),
        yaxis2=dict(
            title="",
            gridcolor=grid_color,
            zeroline=True,
            zerolinecolor=grid_color,
            zerolinewidth=1,
            tickfont=dict(size=10)
        ),
        plot_bgcolor=background_color,
        paper_bgcolor=background_color,
        height=700,  # Augmenté pour accommoder le sous-graphique
        width=950,   # Légèrement plus large pour un meilleur ratio
        margin=dict(l=60, r=60, t=120, b=90),  # Marges ajustées
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.05,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="#d3d3d3",
            borderwidth=1
        ),
        hovermode="x unified"
    )
    
    # Ajouter des annotations avec des statistiques
    total_publications = int(df['count'].sum())
    mean_per_year = df['count'].mean()
    total_citations = int(df['total_citations'].sum())
    avg_citations_per_pub = total_citations / total_publications if total_publications > 0 else 0
    
    fig.add_annotation(
        x=0.25,
        y=1,
        xref="paper",
        yref="paper",
        text=(f"<b>Résumé</b>: {total_publications} publications | "
              f"{mean_per_year:.1f} pub/an | "
              f"{total_citations} citations | "
              f"{avg_citations_per_pub:.1f} citations/pub"),
        showarrow=False,
        font=dict(size=13, color="#34495e"),
        align="left",
        bgcolor="rgba(255, 255, 255, 0.8)",
        bordercolor="#d3d3d3",
        borderwidth=1,
        borderpad=6,
        xanchor="left",
        yanchor="top",
        yshift=-10
    )
    

    return fig

# Exemple d'utilisation
start_year = 2010
end_year = 2022
selected_researcher = "Ilham ALLOUI"  # ou "Tous les chercheurs" ou None
fig_pub = create_perfected_publications_chart(start_year, end_year, selected_researcher)

if fig_pub:
    fig_pub.show()
else:
    print(f"Aucune donnée trouvée pour la période {start_year}-{end_year}")