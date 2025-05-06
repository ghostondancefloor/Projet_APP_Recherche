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

# Affichage du formulaire de connexion si l'utilisateur n'est pas connecté
if not st.session_state['connecte']:
    st.title("Connexion au Dashboard Scientifique")
    
    with st.form("login_form"):
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
            df = viz_module.get_publications_by_year(1970, 2025)  # Plage large pour tout récupérer
            if not df.empty and 'publicationYear' in df.columns:
                return sorted(df['publicationYear'].unique())
        
        # Si échec, retourner une plage par défaut
        return list(range(2000, datetime.now().year + 1))

    # Ajouter un bouton de déconnexion dans la barre latérale
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
         "📈 Visualisations par année", 
         "🔍 Visualisations générales"]
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
                if fig_articles:
                    st.plotly_chart(fig_articles, use_container_width=True)
                else:
                    st.warning(f"Aucune donnée d'articles trouvée")

    # Page 2: Visualisations dépendant uniquement de l'année (accessibles à tous)
    elif page == "📈 Visualisations par année":
        st.title("📈 Visualisations par année")
        st.write(f"**Année sélectionnée**: {selected_year}")
        
        # Visualisation 1: Carte des pays collaborateurs
        st.header("Carte des pays collaborateurs")
        with st.spinner('Chargement des données...'):
            viz1 = import_visualization_module("bddviz1")
            if viz1 and hasattr(viz1, 'create_enhanced_map'):
                fig_map = viz1.create_enhanced_map(selected_year)
                if fig_map:
                    st.plotly_chart(fig_map, use_container_width=True)
                else:
                    st.warning(f"Aucune donnée de pays trouvée pour l'année {selected_year}")
        
        # Visualisation 2: Top 5 des pays collaborateurs
        st.header("Top 5 des pays collaborateurs")
        with st.spinner('Chargement des données...'):
            viz2 = import_visualization_module("bddviz2")
            if viz2 and hasattr(viz2, 'create_top5_countries_chart'):
                fig_top5 = viz2.create_top5_countries_chart(selected_year)
                if fig_top5:
                    st.plotly_chart(fig_top5, use_container_width=True)
                else:
                    st.warning(f"Aucune donnée pour le top 5 des pays en {selected_year}")

    # Page 3: Visualisations indépendantes (accessibles à tous)
    else:
        st.title("🔍 Visualisations générales")
        st.write("Ces visualisations affichent des données générales.")
        
        # Visualisation 6: Graphe de réseau des collaborations
        st.header("Réseau global de collaborations")
        with st.spinner('Chargement des données...'):
            viz6 = import_visualization_module("bddviz6")
            if viz6 and hasattr(viz6, 'create_enhanced_network_graph'):
                fig_network = viz6.create_enhanced_network_graph()
                if fig_network:
                    st.plotly_chart(fig_network, use_container_width=True)
                else:
                    st.warning("Aucune donnée de collaboration trouvée")
        
        # Visualisation 7: Nombre d'institutions collaborées par chercheur
        st.header("Nombre d'institutions par chercheur")
        with st.spinner('Chargement des données...'):
            viz7 = import_visualization_module("bddviz7")
            if viz7 and hasattr(viz7, 'create_simple_institutions_chart'):
                fig_institutions = viz7.create_simple_institutions_chart()
                if fig_institutions:
                    st.plotly_chart(fig_institutions, use_container_width=True)
                else:
                    st.warning("Aucune donnée d'institutions trouvée")
        
        # Visualisation 9: Top 3 chercheurs par citations
        st.header("Top 3 chercheurs par citations")
        with st.spinner('Chargement des données...'):
            viz9 = import_visualization_module("bddviz9")
            if viz9 and hasattr(viz9, 'create_top3_researchers_chart'):
                fig_top3 = viz9.create_top3_researchers_chart()

                if fig_top3:
                    st.plotly_chart(fig_top3, use_container_width=True)
                else:
                    st.warning("Aucune donnée sur les citations trouvée")

    # Pied de page
    st.markdown("---")
    st.markdown(f"*Dernière mise à jour: {time.strftime('%d/%m/%Y %H:%M:%S')}*")