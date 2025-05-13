import streamlit as st
import pandas as pd
import importlib
import sys
import os
from datetime import datetime
import time
import mysql.connector
import hashlib

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Scientifique",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour le style
st.markdown("""
<style>
    /* Background gris clair pour toute la page */
    .stApp {
        background-color: #f0f2f5;
    }
    
    /* Style pour la barre latérale (bleu foncé) */
    [data-testid="stSidebar"] {
        background-color: #1a237e !important;
    }
    
    /* Couleur du texte dans la sidebar */
    [data-testid="stSidebar"] .st-eb,
    [data-testid="stSidebar"] [data-testid="stSidebarNav"],
    [data-testid="stSidebar"] [data-testid="stSidebarNavItems"],
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p {
        color: white !important;
    }
    
    /* Style pour les titres de la sidebar */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: white !important;
    }
    
    /* Style pour les graphiques (ombre portée) */
    .stPlotlyChart {
        box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);
        border-radius: 5px;
        padding: 10px;
        background-color: white;
        margin-bottom: 20px;
        margin: 0 auto 20px auto; /* Centre les graphiques et ajoute une marge en bas */
        overflow: hidden;

    }
    /* Style pour les widgets de la sidebar */
    [data-testid="stSidebar"] .stSlider, 
    [data-testid="stSidebar"] .stSelectbox, 
    [data-testid="stSidebar"] .stRadio {
        color: white !important;
    }
    
    /* Style pour les widgets spécifiques de la sidebar */
    .stSlider [data-testid="stThumbValue"] {
        color: white !important;
    }
    
    /* Assurer que les sliders sont visibles sur fond bleu */
    [data-testid="stSidebar"] .stSlider [data-testid="stThumb"] {
        background-color: white !important;
    }
    
    /* Amélioration des headers */
    h1, h2, h3 {
        color: #1a237e;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    
    /* Style pour les boutons */
    .stButton > button {
        background-color: #1a237e;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
    }
    
    .stButton > button:hover {
        background-color: #303f9f;
    }
    
    /* Style pour le formulaire de login */
    [data-testid="stForm"] {
        background-color: white;
        border-radius: 5px;
        padding: 20px;
        box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
    }
    
    /* Styliser les séparateurs */
    hr {
        margin-top: 30px;
        margin-bottom: 30px;
    }
    .titre-connexion {
    text-align: center;
    color: #1a237e;
    padding-top: 20px;
    padding-bottom: 20px;
    font-size: 2em;}
        
</style>
""", unsafe_allow_html=True)

# Fonction de connexion à la base de données
def connecter_db():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "db"),
            user=os.getenv("DB_USER", "user"),
            password=os.getenv("DB_PASS", "userpass"),
            database=os.getenv("DB_NAME", "dashboarddb"),
            port=int(os.getenv("DB_PORT", "3306"))
        )
        return conn
    except mysql.connector.Error as err:
        st.error(f"Erreur de connexion à la base de données: {err}")
        return None


# Fonction pour vérifier les identifiants et récupérer les infos du chercheur
def verifier_identifiants(email, mot_de_passe):
    conn = connecter_db()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        # Requête pour vérifier si le chercheur existe
        query = "SELECT * FROM chercheurs WHERE email = %s AND mot_de_passe = %s"
        cursor.execute(query, (email, mot_de_passe))
        
        chercheur = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return chercheur
    except mysql.connector.Error as err:
        st.error(f"Erreur lors de la vérification des identifiants: {err}")
        if conn:
            conn.close()
        return None

# Session state pour gérer la connexion
if 'connecte' not in st.session_state:
    st.session_state['connecte'] = False
if 'chercheur_info' not in st.session_state:
    st.session_state['chercheur_info'] = None
if 'est_admin' not in st.session_state:
    st.session_state['est_admin'] = False

# Création d'un conteneur pour le formulaire de connexion avec style amélioré
if not st.session_state['connecte']:
    st.markdown('<h1 class="titre-connexion">Connexion au Dashboard Scientifique</h1>', unsafe_allow_html=True)
    
    # Conteneur avec une disposition soignée pour le formulaire
    login_container = st.container()
    with login_container:
        # Ajouter un espace sur les côtés
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                st.write("### Veuillez vous connecter")
                email = st.text_input("Email")
                mot_de_passe = st.text_input("Mot de passe", type="password")
                submit_button = st.form_submit_button("Se connecter")
                
                if submit_button:
                    chercheur = verifier_identifiants(email, mot_de_passe)
                    if chercheur:
                        st.session_state['connecte'] = True
                        st.session_state['chercheur_info'] = chercheur
                        # Vérifier si l'utilisateur est un administrateur (ajoutez une colonne est_admin dans votre table)
                        st.session_state['est_admin'] = chercheur.get('est_admin', False) if chercheur else False
                        st.success("Connexion réussie! Redirection vers le dashboard...")
                        st.rerun()  # Remplacé st.experimental_rerun() par st.rerun()
                    else:
                        st.error("Email ou mot de passe incorrect.")

# Le reste du code dashboard s'exécute uniquement si l'utilisateur est connecté
if st.session_state['connecte']:
    # Récupérer les infos du chercheur connecté
    chercheur_connecte = st.session_state['chercheur_info']
    nom_chercheur = f"{chercheur_connecte.get('prenom', '')} {chercheur_connecte.get('nom', '')}" if chercheur_connecte else "Inconnu"
    
    # Fonction pour lire la liste des chercheurs autorisés
    def lire_chercheurs_autorises(fichier):
        try:
            with open(fichier, "r", encoding="utf-8") as f:
                chercheurs = [ligne.strip() for ligne in f if ligne.strip()]
            return chercheurs
        except FileNotFoundError:
            st.error(f"Fichier non trouvé : {fichier}")
            return []

    # Import dynamique des modules de visualisation
    def import_visualization_module(module_name):
        try:
            # Ajouter le répertoire courant au chemin de recherche des modules si nécessaire
            current_dir = os.path.dirname(os.path.abspath(__file__))
            if current_dir not in sys.path:
                sys.path.append(current_dir)
                
            # Importer le module
            module = importlib.import_module(module_name)
            return module
        except ImportError as e:
            st.error(f"Erreur lors de l'importation du module {module_name}: {e}")
            return None

    # Fonction pour obtenir les années disponibles dans la base de données
    @st.cache_data
    def get_available_years():
        # Importer le module qui contient la fonction pour obtenir les années
        viz_module = import_visualization_module("bddviz3")  # Module des publications par année
        
        if hasattr(viz_module, 'get_publications_by_year'):
            # Récupérer toutes les années où il y a des publications
            df = viz_module.get_publications_by_year(1974, 2024)  # Plage large pour tout récupérer
            if not df.empty and 'publicationYear' in df.columns:
                return sorted(df['publicationYear'].unique())
        
        # Si échec, retourner une plage par défaut
        return list(range(2000, datetime.now().year + 1))

    # Fonction pour styliser un graphique avec des ombres
    def styliser_graphique(fig):
        if fig:
            # Définir un style de fond pour les graphiques
            fig.update_layout(
                paper_bgcolor='white',
                plot_bgcolor='rgba(240, 242, 245, 0.5)',
                font=dict(color='#333'),
                margin=dict(l=25, r=25, t=40, b=25),  # Marges réduites pour des graphiques plus compacts
                height=400,  # Hauteur fixe réduite pour tous les graphiques
            )
        return fig

    # Ajouter un bouton de déconnexion dans la barre latérale avec style amélioré
    st.sidebar.title(f"Bienvenue, {nom_chercheur}")
    if st.sidebar.button("Déconnexion"):
        st.session_state['connecte'] = False
        st.session_state['chercheur_info'] = None
        st.session_state['est_admin'] = False
        st.rerun()  # Remplacé st.experimental_rerun() par st.rerun()

    # Charger les chercheurs autorisés
    chercheurs_autorises = lire_chercheurs_autorises("researchers.txt")
    years = get_available_years()

    # Barre latérale avec filtres
    st.sidebar.title("Filtres")

    # Ajout d'un sélecteur de page
    page = st.sidebar.radio(
        "Naviguer vers:",
        ["📊 Mes publications et collaborations", 
         "🌍 Visualisations générales"]  # Pages fusionnées
    )

    # Filtres communs
    min_year, max_year = min(years), max(years)
    selected_year = st.sidebar.slider(
        "Sélectionnez une année", 
        min_value=min_year, 
        max_value=max_year, 
        value=max_year
    )

    # Période pour certaines visualisations
    start_year, end_year = st.sidebar.slider(
        "Période de publication",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year)
    )

    # Pour les administrateurs seulement: sélection de chercheur
    selected_researcher = None
    if st.session_state['est_admin']:
        selected_researcher = st.sidebar.selectbox(
            "Sélectionnez un chercheur",
            options=["Tous les chercheurs"] + chercheurs_autorises
        )
    else:
        # Pour les chercheurs normaux, on filtre automatiquement sur leur nom
        selected_researcher = nom_chercheur.strip()

    # Conteneur principal avec padding
    main_container = st.container()
    with main_container:
        # Page 1: Visualisations personnelles (filtrées par chercheur connecté)
        if page == "📊 Mes publications et collaborations":
            st.title("📊 Mes publications et collaborations")
            st.write(f"**Période**: {start_year}-{end_year}")
            
            # Visualisation 3: Publications par année et chercheur
            st.header("Mes publications par année")
            with st.spinner('Chargement des données...'):
                viz3 = import_visualization_module("bddviz3")
                if viz3 and hasattr(viz3, 'create_perfected_publications_chart'):
                    fig_pub = viz3.create_perfected_publications_chart(start_year, end_year, selected_researcher)
                    fig_pub = styliser_graphique(fig_pub)  # Ajout du style
                    if fig_pub:
                        st.plotly_chart(fig_pub, use_container_width=True)
                    else:
                        st.warning(f"Aucune donnée de publication trouvée pour la période {start_year}-{end_year}")
            
            # Visualisation 4: Diagramme de Sankey
            st.header("Diagramme de Sankey de mes collaborations")
            with st.spinner('Chargement des données...'):
                viz4 = import_visualization_module("bddviz4")
                if viz4 and hasattr(viz4, 'generate_improved_sankey'):
                    fig_sankey = viz4.generate_improved_sankey(selected_researcher)
                    fig_sankey = styliser_graphique(fig_sankey)  # Ajout du style
                    if fig_sankey:
                        st.plotly_chart(fig_sankey, use_container_width=True)
                    else:
                        st.warning(f"Aucune donnée Sankey trouvée")
            
            # Visualisation 5: Top 10 Universités
            st.header("Top 10 Universités avec lesquelles j'ai collaboré")
            with st.spinner('Chargement des données...'):
                viz5 = import_visualization_module("bddviz5")
                if viz5 and hasattr(viz5, 'create_perfected_university_chart'):
                    fig_university = viz5.create_perfected_university_chart(selected_researcher, start_year, end_year)
                    fig_university = styliser_graphique(fig_university)  # Ajout du style
                    if fig_university:
                        st.plotly_chart(fig_university, use_container_width=True)
                    else:
                        st.warning(f"Aucune donnée d'université trouvée entre {start_year} et {end_year}")
            
            # Visualisation 8: Top 5 articles les plus cités
            st.header("Mes 5 articles les plus cités")
            with st.spinner('Chargement des données...'):
                viz8 = import_visualization_module("bddviz8")
                if viz8 and hasattr(viz8, 'create_improved_top_articles_chart'):
                    fig_articles = viz8.create_improved_top_articles_chart(selected_researcher)
                    fig_articles = styliser_graphique(fig_articles)  # Ajout du style
                    if fig_articles:
                        st.plotly_chart(fig_articles, use_container_width=True)
                    else:
                        st.warning(f"Aucune donnée d'articles trouvée")

        # Page fusionnée: Visualisations générales et par année
        else:
            st.title("🌍 Visualisations générales")
            
            # Créer des onglets pour organiser les visualisations
            tab1, tab2 = st.tabs(["Visualisations par année", "Visualisations globales"])
            
            with tab1:
                st.header(f"Visualisations pour l'année {selected_year}")
                
                # Visualisation 1: Carte des pays collaborateurs (avec filtre année)
                st.subheader("Carte des pays collaborateurs")
                with st.spinner('Chargement des données...'):
                    viz1 = import_visualization_module("bddviz1")
                    if viz1 and hasattr(viz1, 'create_enhanced_map'):
                        fig_map = viz1.create_enhanced_map(selected_year)
                        fig_map = styliser_graphique(fig_map)
                        if fig_map:
                            st.plotly_chart(fig_map, use_container_width=True)
                        else:
                            st.warning(f"Aucune donnée de pays trouvée pour l'année {selected_year}")
                
                # Visualisation 2: Top 5 des pays collaborateurs
                st.subheader("Top 5 des pays collaborateurs")
                with st.spinner('Chargement des données...'):
                    viz2 = import_visualization_module("bddviz2")
                    if viz2 and hasattr(viz2, 'create_top5_countries_chart'):
                        fig_top5 = viz2.create_top5_countries_chart(selected_year)
                        fig_top5 = styliser_graphique(fig_top5)
                        if fig_top5:
                            st.plotly_chart(fig_top5, use_container_width=True)
                        else:
                            st.warning(f"Aucune donnée pour le top 5 des pays en {selected_year}")
            
            with tab2:
                st.header("Visualisations globales")
                
                # Visualisation 6: Graphe de réseau des collaborations
                st.subheader("Réseau global de collaborations")
                with st.spinner('Chargement des données...'):
                    viz6 = import_visualization_module("bddviz6")
                    if viz6 and hasattr(viz6, 'create_enhanced_network_graph'):
                        fig_network = viz6.create_enhanced_network_graph()
                        fig_network = styliser_graphique(fig_network)
                        if fig_network:
                            st.plotly_chart(fig_network, use_container_width=True)
                        else:
                            st.warning("Aucune donnée de collaboration trouvée")
                
                # Visualisation 7: Nombre d'institutions collaborées par chercheur
                st.subheader("Nombre d'institutions par chercheur")
                with st.spinner('Chargement des données...'):
                    viz7 = import_visualization_module("bddviz7")
                    if viz7 and hasattr(viz7, 'create_simple_institutions_chart'):
                        fig_institutions = viz7.create_simple_institutions_chart()
                        fig_institutions = styliser_graphique(fig_institutions)
                        if fig_institutions:
                            st.plotly_chart(fig_institutions, use_container_width=True)
                        else:
                            st.warning("Aucune donnée d'institutions trouvée")
                
                # Visualisation 9: Top 3 chercheurs par citations
                st.subheader("Top 3 chercheurs par citations")
                with st.spinner('Chargement des données...'):
                    viz9 = import_visualization_module("bddviz9")
                    if viz9 and hasattr(viz9, 'create_top3_researchers_chart'):
                        fig_top3 = viz9.create_top3_researchers_chart()
                        fig_top3 = styliser_graphique(fig_top3)
                        if fig_top3:
                            st.plotly_chart(fig_top3, use_container_width=True)
                        else:
                            st.warning("Aucune donnée sur les citations trouvée")

    # Pied de page
    st.markdown("---")
    st.markdown(f"*Dernière mise à jour: {time.strftime('%d/%m/%Y %H:%M:%S')}*")