import requests
import requests
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

API_URL="http://localhost:8000"


def get_token(user: str, mdp: str):
    print(f"Obtention du token pour {user} avec mdp {mdp}...")
    r=requests.post(f"{API_URL}/token", data={"username": user, "password": mdp})
    if r.status_code!=200:
        raise Exception(f"Erreur d'authentification : {r.text}")
    return r.json()["access_token"]

def get_infos_chercheur(nom: str, token: str):
    print(f"Récupération des publications pour {nom} avec token {token}...")
    headers={"Authorization": f"Bearer {token}"}
    r=requests.get(f"{API_URL}/api/chercheurs/{nom}", headers=headers)
    if r.status_code!=200:
        raise Exception(f"Erreur API : {r.text}")
    return r.json()



def recuperation_infos_chercheur(nom, user, mdp, n_clusters=3):
    # recupération des articles pour le chercheur
    token=get_token(user, mdp)
    infos=get_infos_chercheur(nom, token)
    if not infos:
        return {"error": "Aucune info trouvée pour ce chercheur."}

    # extraction des titres des articles
    titres=[pub["titre"] for pub in infos["publications"]]
    print(f"{len(titres)} titres récupérés pour {nom}.")

