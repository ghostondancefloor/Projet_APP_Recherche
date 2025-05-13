#!/usr/bin/env python3
"""
Script pour transformer les données sources en fichiers JSON structurés
qui pourront ensuite être importés dans MongoDB.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Union

# Dossier de sortie pour les fichiers transformés
DOSSIER_SORTIE = 'transformed_data'

# Chemins des fichiers d'entrée
FICHIERS_JSON = [
    'DASHBOARD/data.json',
    'DASHBOARD/aggregated_data.json',
    'DASHBOARD/assets/graph_edges.json', 
    'DASHBOARD/assets/hal_results_cleaned.json',
    'DASHBOARD/assets/sankey_data.json'
]

def lire_fichier_json(chemin_fichier: str) -> Union[List[Dict], Dict]:
    """Lit un fichier JSON et retourne son contenu."""
    try:
        with open(chemin_fichier, 'r', encoding='utf-8') as fichier:
            return json.load(fichier)
    except FileNotFoundError:
        print(f"Attention: Fichier {chemin_fichier} non trouvé. Ignoré.")
        return []
    except json.JSONDecodeError:
        print(f"Erreur: Impossible de parser {chemin_fichier} comme JSON. Ignoré.")
        return []
    except Exception as e:
        print(f"Erreur lors de la lecture de {chemin_fichier}: {str(e)}. Ignoré.")
        return []

def extraire_chercheurs(data_json, hal_results_json, graph_edges_json, sankey_json):
    """Extrait et transforme les données des chercheurs."""
    chercheurs = {}
    
    # Extraction depuis data.json
    if data_json:
        print(f"Traitement de {len(data_json)} entrées depuis data.json")
        for item in data_json:
            if 'researcher' in item:
                nom_chercheur = item['researcher']
                if nom_chercheur not in chercheurs:
                    chercheurs[nom_chercheur] = {
                        "nom": nom_chercheur,
                        "publications": [],
                        "collaborateurs": [],
                        "institutions": [],
                        "date_creation": datetime.now().isoformat()
                    }
                
                # Ajouter publication si elle existe
                if 'title' in item:
                    chercheurs[nom_chercheur]['publications'].append({
                        "titre": item['title'],
                        "annee": item.get('year'),
                        "citations": item.get('value of cited by')
                    })
                
                # Ajouter collaborateurs depuis la liste d'auteurs
                if 'authors' in item:
                    auteurs = [auteur.strip() for auteur in item['authors'].split(',')]
                    for auteur in auteurs:
                        if auteur != nom_chercheur and auteur not in chercheurs[nom_chercheur]['collaborateurs']:
                            chercheurs[nom_chercheur]['collaborateurs'].append(auteur)
    
    # Extraction depuis hal_results_cleaned.json
    if hal_results_json:
        print(f"Traitement de {len(hal_results_json)} entrées depuis hal_results_cleaned.json")
        for item in hal_results_json:
            if 'name' in item and 'results' in item:
                nom_chercheur = item['name']
                if nom_chercheur not in chercheurs:
                    chercheurs[nom_chercheur] = {
                        "nom": nom_chercheur,
                        "publications": [],
                        "collaborateurs": [],
                        "institutions": [],
                        "date_creation": datetime.now().isoformat()
                    }
                
                # Traitement des résultats
                for result in item['results']:
                    # Ajouter institutions
                    if 'instStructName_s' in result:
                        for inst in result['instStructName_s']:
                            if inst not in chercheurs[nom_chercheur]['institutions']:
                                chercheurs[nom_chercheur]['institutions'].append(inst)
                    
                    # Ajouter publications
                    if 'title_s' in result and result['title_s']:
                        pub_data = {
                            "titre": result['title_s'][0],
                            "annee": result.get('publicationDate_s', '').split('-')[0] if 'publicationDate_s' in result else None
                        }
                        chercheurs[nom_chercheur]['publications'].append(pub_data)
                    
                    # Ajouter collaborateurs
                    if 'authFullName_s' in result:
                        for auteur in result['authFullName_s']:
                            if auteur != nom_chercheur and auteur not in chercheurs[nom_chercheur]['collaborateurs']:
                                chercheurs[nom_chercheur]['collaborateurs'].append(auteur)
    
    # Extraction des collaborations depuis graph_edges.json
    if graph_edges_json:
        print(f"Traitement de {len(graph_edges_json)} entrées depuis graph_edges.json")
        for edge in graph_edges_json:
            if 'source' in edge and 'target' in edge:
                source = edge['source']
                target = edge['target']
                
                # Ajouter chercheurs s'ils n'existent pas
                for nom in [source, target]:
                    if nom not in chercheurs:
                        chercheurs[nom] = {
                            "nom": nom,
                            "publications": [],
                            "collaborateurs": [],
                            "institutions": [],
                            "date_creation": datetime.now().isoformat()
                        }
                
                # Ajouter collaborateurs
                if target not in chercheurs[source]['collaborateurs']:
                    chercheurs[source]['collaborateurs'].append(target)
                if source not in chercheurs[target]['collaborateurs']:
                    chercheurs[target]['collaborateurs'].append(source)
    
    # Extraction depuis Sankey data
    if sankey_json:
        print(f"Traitement de {len(sankey_json)} entrées depuis sankey_data.json")
        for item in sankey_json:
            if 'source' in item and 'target' in item:
                if item['target'].startswith('Institut') or 'Université' in item['target']:
                    # C'est probablement une connexion chercheur->institution
                    nom_chercheur = item['source']
                    nom_institution = item['target']
                    
                    if nom_chercheur not in chercheurs:
                        chercheurs[nom_chercheur] = {
                            "nom": nom_chercheur,
                            "publications": [],
                            "collaborateurs": [],
                            "institutions": [],
                            "date_creation": datetime.now().isoformat()
                        }
                    
                    if nom_institution not in chercheurs[nom_chercheur]['institutions']:
                        chercheurs[nom_chercheur]['institutions'].append(nom_institution)
    
    print(f"Total de {len(chercheurs)} chercheurs extraits")
    return list(chercheurs.values())

def extraire_publications(data_json, hal_results_json):
    """Extrait et transforme les données des publications."""
    publications = {}
    
    # Extraction depuis data.json
    if data_json:
        print(f"Traitement de {len(data_json)} entrées de publications depuis data.json")
        for item in data_json:
            if 'title' in item:
                titre = item['title']
                if titre not in publications:
                    publications[titre] = {
                        "titre": titre,
                        "auteurs": [],
                        "annee": item.get('year'),
                        "citations": item.get('value of cited by'),
                        "mots_cles": [],
                        "institutions": [],
                        "date_creation": datetime.now().isoformat()
                    }
                
                # Ajouter auteurs
                if 'authors' in item:
                    auteurs = [auteur.strip() for auteur in item['authors'].split(',')]
                    for auteur in auteurs:
                        if auteur not in publications[titre]['auteurs']:
                            publications[titre]['auteurs'].append(auteur)
                
                # Ajouter chercheur comme auteur s'il n'est pas déjà dans la liste
                if 'researcher' in item and item['researcher'] not in publications[titre]['auteurs']:
                    publications[titre]['auteurs'].append(item['researcher'])
    
    # Extraction depuis hal_results_cleaned.json
    if hal_results_json:
        print(f"Traitement de publications depuis {len(hal_results_json)} entrées HAL")
        for item in hal_results_json:
            if 'results' in item:
                for result in item['results']:
                    if 'title_s' in result and result['title_s']:
                        titre = result['title_s'][0]
                        
                        # Créer la publication si elle n'existe pas
                        if titre not in publications:
                            annee = result.get('publicationDate_s', '').split('-')[0] if 'publicationDate_s' in result else None
                            publications[titre] = {
                                "titre": titre,
                                "auteurs": [],
                                "annee": annee,
                                "citations": None,
                                "mots_cles": [],
                                "institutions": [],
                                "date_creation": datetime.now().isoformat()
                            }
                        
                        # Ajouter auteurs
                        if 'authFullName_s' in result:
                            for auteur in result['authFullName_s']:
                                if auteur not in publications[titre]['auteurs']:
                                    publications[titre]['auteurs'].append(auteur)
                        
                        # Ajouter chercheur comme auteur s'il n'est pas déjà dans la liste
                        if 'name' in item and item['name'] not in publications[titre]['auteurs']:
                            publications[titre]['auteurs'].append(item['name'])
                        
                        # Ajouter institutions
                        if 'instStructName_s' in result:
                            for inst in result['instStructName_s']:
                                if inst not in publications[titre]['institutions']:
                                    publications[titre]['institutions'].append(inst)
                        
                        # Ajouter domaine comme mot-clé
                        if 'primaryDomain_s' in result:
                            domaine = result['primaryDomain_s']
                            if domaine not in publications[titre]['mots_cles']:
                                publications[titre]['mots_cles'].append(domaine)
    
    print(f"Total de {len(publications)} publications extraites")
    return list(publications.values())

def extraire_institutions(hal_results_json, sankey_json):
    """Extrait et transforme les données des institutions."""
    institutions = {}
    
    # Extraction depuis hal_results_cleaned.json
    if hal_results_json:
        print(f"Traitement d'institutions depuis {len(hal_results_json)} entrées HAL")
        for item in hal_results_json:
            if 'results' in item:
                nom_chercheur = item.get('name')
                
                for result in item['results']:
                    if 'instStructName_s' in result:
                        for nom_inst in result['instStructName_s']:
                            if nom_inst not in institutions:
                                institutions[nom_inst] = {
                                    "nom": nom_inst,
                                    "pays": None,
                                    "type": "académique" if "Université" in nom_inst or "Institut" in nom_inst else "autre",
                                    "chercheurs": [],
                                    "publications": [],
                                    "date_creation": datetime.now().isoformat()
                                }
                            
                            # Définir le pays si disponible
                            if 'structCountry_s' in result and result['structCountry_s']:
                                institutions[nom_inst]['pays'] = result['structCountry_s'][0]
                            
                            # Ajouter chercheur
                            if nom_chercheur and nom_chercheur not in institutions[nom_inst]['chercheurs']:
                                institutions[nom_inst]['chercheurs'].append(nom_chercheur)
                            
                            # Ajouter publication
                            if 'title_s' in result and result['title_s']:
                                titre_pub = result['title_s'][0]
                                if titre_pub not in institutions[nom_inst]['publications']:
                                    institutions[nom_inst]['publications'].append(titre_pub)
    
    # Extraction depuis sankey_data.json
    if sankey_json:
        print(f"Traitement d'institutions depuis {len(sankey_json)} entrées Sankey")
        for item in sankey_json:
            if 'source' in item and 'target' in item and 'value' in item:
                if item['target'].startswith('Institut') or 'Université' in item['target']:
                    # C'est probablement une connexion chercheur->institution
                    nom_chercheur = item['source']
                    nom_institution = item['target']
                    
                    if nom_institution not in institutions:
                        institutions[nom_institution] = {
                            "nom": nom_institution,
                            "pays": None,
                            "type": "académique" if "Université" in nom_institution or "Institut" in nom_institution else "autre",
                            "chercheurs": [],
                            "publications": [],
                            "date_creation": datetime.now().isoformat()
                        }
                    
                    if nom_chercheur not in institutions[nom_institution]['chercheurs']:
                        institutions[nom_institution]['chercheurs'].append(nom_chercheur)
    
    print(f"Total de {len(institutions)} institutions extraites")
    return list(institutions.values())

def extraire_collaborations(graph_edges_json):
    """Extrait et transforme les données de collaboration."""
    collaborations = []
    
    if graph_edges_json:
        print(f"Traitement de {len(graph_edges_json)} collaborations depuis graph_edges.json")
        for edge in graph_edges_json:
            if 'source' in edge and 'target' in edge and 'weight' in edge:
                collab = {
                    "chercheur1": edge['source'],
                    "chercheur2": edge['target'],
                    "poids": edge['weight'],
                    "publications": [],  # Serait rempli avec les IDs de publications réelles
                    "premiere_collaboration": None,  # Nécessiterait des données de date réelles
                    "derniere_collaboration": None,  # Nécessiterait des données de date réelles
                    "date_creation": datetime.now().isoformat()
                }
                collaborations.append(collab)
    
    print(f"Total de {len(collaborations)} collaborations extraites")
    return collaborations

def extraire_stats_pays(agraggated_data_json):
    """Extrait et transforme les statistiques par pays."""
    stats_pays = []
    
    if agraggated_data_json:
        print(f"Traitement de {len(agraggated_data_json)} entrées de statistiques par pays")
        for donnees_annee in agraggated_data_json:
            if 'year' in donnees_annee and 'countries' in donnees_annee:
                annee = donnees_annee['year']
                for donnees_pays in donnees_annee['countries']:
                    if 'country' in donnees_pays and 'count' in donnees_pays:
                        stat = {
                            "pays": donnees_pays['country'],
                            "annee": annee,
                            "nombre_publications": donnees_pays['count'],
                            "nombre_chercheurs": None,  # Nécessiterait des données supplémentaires
                            "nombre_citations": None,   # Nécessiterait des données supplémentaires
                            "principales_institutions": [],  # Nécessiterait des données supplémentaires
                            "date_creation": datetime.now().isoformat()
                        }
                        stats_pays.append(stat)
    
    print(f"Total de {len(stats_pays)} statistiques pays extraites")
    return stats_pays

def enregistrer_en_json(donnees, nom_fichier):
    """Enregistre les données dans un fichier JSON."""
    # Créer le dossier de sortie s'il n'existe pas
    if not os.path.exists(DOSSIER_SORTIE):
        os.makedirs(DOSSIER_SORTIE)
        
    chemin_complet = os.path.join(DOSSIER_SORTIE, nom_fichier)
    
    try:
        with open(chemin_complet, 'w', encoding='utf-8') as fichier:
            json.dump(donnees, fichier, ensure_ascii=False, indent=2)
        print(f"✅ Fichier {chemin_complet} créé avec succès")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'enregistrement de {chemin_complet}: {str(e)}")
        return False

def transformer_donnees():
    """Transforme les données sources et les enregistre en fichiers JSON."""
    try:
        # Charger toutes les données
        print("\nChargement des fichiers JSON sources...")
        data_json = lire_fichier_json(FICHIERS_JSON[0])
        agraggated_data_json = lire_fichier_json(FICHIERS_JSON[1])
        graph_edges_json = lire_fichier_json(FICHIERS_JSON[2])
        hal_results_json = lire_fichier_json(FICHIERS_JSON[3])
        sankey_json = lire_fichier_json(FICHIERS_JSON[4])
        
        # Extraire les données transformées
        print("\nTransformation des données...")
        chercheurs = extraire_chercheurs(data_json, hal_results_json, graph_edges_json, sankey_json)
        publications = extraire_publications(data_json, hal_results_json)
        institutions = extraire_institutions(hal_results_json, sankey_json)
        collaborations = extraire_collaborations(graph_edges_json)
        stats_pays = extraire_stats_pays(agraggated_data_json)
        
        # Enregistrer les données transformées
        print("\nEnregistrement des fichiers JSON transformés...")
        fichiers_crees = 0
        if chercheurs:
            if enregistrer_en_json(chercheurs, 'chercheurs.json'):
                fichiers_crees += 1
        
        if publications:
            if enregistrer_en_json(publications, 'publications.json'):
                fichiers_crees += 1
        
        if institutions:
            if enregistrer_en_json(institutions, 'institutions.json'):
                fichiers_crees += 1
        
        if collaborations:
            if enregistrer_en_json(collaborations, 'collaborations.json'):
                fichiers_crees += 1
        
        if stats_pays:
            if enregistrer_en_json(stats_pays, 'stats_pays.json'):
                fichiers_crees += 1
        
        print(f"\nTransformation terminée. {fichiers_crees} fichiers JSON créés dans le dossier '{DOSSIER_SORTIE}'")
        
    except Exception as e:
        print(f"\nErreur pendant la transformation : {str(e)}")

def verifier_fichiers_source():
    """Vérifie l'existence des fichiers source."""
    print("Vérification des fichiers source...")
    fichiers_manquants = 0
    
    for chemin in FICHIERS_JSON:
        if os.path.exists(chemin):
            print(f"✅ Le fichier {chemin} existe")
        else:
            print(f"❌ Le fichier {chemin} n'existe pas")
            fichiers_manquants += 1
    
    if fichiers_manquants > 0:
        print(f"\n⚠️ {fichiers_manquants} fichier(s) source(s) manquant(s).")
        print("Vérifiez les chemins d'accès ou créez le dossier DASHBOARD avec les fichiers nécessaires.")
    
    return fichiers_manquants == 0

def main():
    print("=== Transformation des données en fichiers JSON ===")
    print(f"Répertoire de travail actuel : {os.getcwd()}")
    
    # Vérifier l'existence des fichiers source avant de continuer
    if verifier_fichiers_source():
        transformer_donnees()
    else:
        print("\n⚠️ La transformation est interrompue en raison de fichiers manquants.")
        print("Suggestion: Créez la structure de dossiers suivante avec vos fichiers JSON:")
        print("- DASHBOARD/")
        print("  |- data.json")
        print("  |- aggregated_data.json")
        print("  |- assets/")
        print("    |- graph_edges.json")
        print("    |- hal_results_cleaned.json")
        print("    |- sankey_data.json")

if __name__ == "__main__":
    main()