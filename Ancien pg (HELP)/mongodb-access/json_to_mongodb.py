#!/usr/bin/env python3
"""
Script pour importer les fichiers JSON transformés dans MongoDB.
À exécuter après avoir généré les fichiers avec le script de transformation.
"""

import json
import os
from pymongo import MongoClient
import sys

# Dossier contenant les fichiers JSON transformés
DOSSIER_ENTREE = 'transformed_data'

# Fichiers à importer
FICHIERS_JSON = [
    'chercheurs.json',
    'publications.json',
    'institutions.json',
    'collaborations.json',
    'stats_pays.json'
]

# Paramètres de connexion MongoDB
MONGO_URI = "mongodb://localhost:27017/"
NOM_DB = "research_db_structure"  # Nom de la base de données

def lire_fichier_json(chemin_fichier):
    """Lit un fichier JSON et retourne son contenu."""
    try:
        with open(chemin_fichier, 'r', encoding='utf-8') as fichier:
            return json.load(fichier)
    except FileNotFoundError:
        print(f"Erreur: Fichier {chemin_fichier} non trouvé.")
        return None
    except json.JSONDecodeError as e:
        print(f"Erreur: Impossible de parser {chemin_fichier} comme JSON: {e}")
        return None
    except Exception as e:
        print(f"Erreur lors de la lecture de {chemin_fichier}: {str(e)}")
        return None

def importer_dans_mongodb(donnees, nom_collection, uri, nom_db):
    """Importe les données dans une collection MongoDB."""
    if not donnees:
        print(f"Aucune donnée à importer pour {nom_collection}")
        return 0
    
    try:
        # Connexion à MongoDB
        client = MongoClient(uri)
        db = client[nom_db]
        collection = db[nom_collection]
        
        # Supprimer les documents existants (optionnel)
        collection.delete_many({})
        
        # Insérer les nouvelles données
        if isinstance(donnees, list):
            if len(donnees) > 0:
                result = collection.insert_many(donnees)
                return len(result.inserted_ids)
            else:
                return 0
        else:
            # Si les données ne sont pas une liste, les convertir en liste
            result = collection.insert_one(donnees)
            return 1
    except Exception as e:
        print(f"Erreur lors de l'importation dans MongoDB: {str(e)}")
        return 0
    finally:
        if 'client' in locals():
            client.close()

def creer_indexes(uri, nom_db):
    """Crée des index pour améliorer les performances des requêtes."""
    try:
        client = MongoClient(uri)
        db = client[nom_db]
        
        # Créer des index sur les champs fréquemment recherchés
        db.chercheurs.create_index("nom")
        db.publications.create_index("titre")
        db.publications.create_index("annee")
        db.institutions.create_index("nom")
        db.stats_pays.create_index([("pays", 1), ("annee", 1)])
        
    except Exception as e:
        print(f"Erreur lors de la création des index: {str(e)}")
    finally:
        if 'client' in locals():
            client.close()

def verifier_mongodb():
    """Vérifie que MongoDB est accessible."""
    print("\n--- Vérification de la connexion MongoDB ---")
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        server_info = client.server_info()
        print(f"✅ Connecté à MongoDB version: {server_info.get('version')}")
        client.close()
        return True
    except Exception as e:
        print(f"Erreur de connexion à MongoDB: {str(e)}")
        return False

def verifier_dossier_entree():
    """Vérifie que le dossier d'entrée existe et contient les fichiers nécessaires."""
    print("\n--- Vérification des fichiers transformés ---")
    
    if not os.path.exists(DOSSIER_ENTREE):
        print(f"Le dossier {DOSSIER_ENTREE} n'existe pas.")
        return False
    
    fichiers_manquants = 0
    for fichier in FICHIERS_JSON:
        chemin_fichier = os.path.join(DOSSIER_ENTREE, fichier)
        if os.path.exists(chemin_fichier):
            taille = os.path.getsize(chemin_fichier)
            print(f"Le fichier {fichier} existe (taille: {taille} octets)")
        else:
            print(f"Le fichier {fichier} n'existe pas")
            fichiers_manquants += 1
    
    return fichiers_manquants == 0

def main():
    print("=== Importation des fichiers JSON vers MongoDB ===")
    print(f"Répertoire de travail actuel: {os.getcwd()}")
    
    # Vérifier que MongoDB est accessible
    if not verifier_mongodb():
        print("Impossible de se connecter à MongoDB. Vérifiez que le serveur est en cours d'exécution.")
        sys.exit(1)
    
    # Vérifier que le dossier d'entrée existe et contient les fichiers nécessaires
    if not verifier_dossier_entree():
        reponse = input("Voulez-vous continuer quand même avec les fichiers disponibles? (o/n): ")
        if reponse.lower() != 'o':
            sys.exit(1)
    
    # Importer chaque fichier JSON dans MongoDB
    documents_importes_total = 0
    collections_importees = 0
    
    for fichier in FICHIERS_JSON:
        chemin_fichier = os.path.join(DOSSIER_ENTREE, fichier)
        nom_collection = os.path.splitext(fichier)[0]  # Nom du fichier sans extension
        
        if not os.path.exists(chemin_fichier):
            print(f"\nIgnoré: {fichier} (fichier non trouvé)")
            continue
            
        print(f"\nTraitement de {fichier} -> collection {nom_collection}...")
        
        # Lire le fichier JSON
        donnees = lire_fichier_json(chemin_fichier)
        if donnees is None:
            print(f"Ignorer {fichier} en raison d'erreurs")
            continue
        
        # Importer dans MongoDB
        nb_documents = importer_dans_mongodb(donnees, nom_collection, MONGO_URI, NOM_DB)
        print(f" {nb_documents} documents importés dans la collection {nom_collection}")
        
        documents_importes_total += nb_documents
        collections_importees += 1
    
    # Créer des index pour améliorer les performances
    if collections_importees > 0:
        print("\nCréation d'index pour optimiser les performances...")
        creer_indexes(MONGO_URI, NOM_DB)
    
    print(f"\n=== Importation terminée ===")
    print(f"{documents_importes_total} documents importés dans {collections_importees} collections")
    print(f"Base de données: {NOM_DB}")
    

if __name__ == "__main__":
    main()