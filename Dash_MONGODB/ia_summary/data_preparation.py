import requests
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from transformers import pipeline
import pandas as pd


API_URL="http://localhost:8000"
model=SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
summarizer=pipeline("summarization", model="facebook/bart-large-cnn")


def get_token(user: str, mdp: str):
    print(f"Obtention du token pour {user} avec mdp {mdp} en cours")
    r=requests.post(f"{API_URL}/token", data={"username": user, "password": mdp})
    if r.status_code!=200:
        raise Exception(f"Erreur d'authentification : {r.text}")
    return r.json()["access_token"]

def get_infos_chercheur(nom: str, token: str):
    print(f"Récupération des publications pour {nom} avec token {token} en cours")
    headers={"Authorization": f"Bearer {token}"}
    r=requests.get(f"{API_URL}/api/chercheurs/{nom}", headers=headers)
    if r.status_code!=200:
        raise Exception(f"Erreur API : {r.text}")
    return r.json()

def generer_embeddings(texte):
    print("Calcul des embeddings en cours")
    return model.encode(texte)

def cluster_embeddings(embeddings, n_clusters=3):
    print(f"Clustering en {n_clusters} thèmes en cours")
    kmeans=KMeans(n_clusters=n_clusters, random_state=42)
    labels=kmeans.fit_predict(embeddings)
    return labels

def generer_summary(texte, summarizer, max_length, min_length):
    texte=texte.strip()
    nb_mots=len(texte.split())

    # tronquer le texte pour éviter les erreurs de longueur
    ### TODO ###
    # gérer ce cas : tronquer par morceaux et faire plusieurs résumés puis résumer les résumés ?
    # modifier le nombre de cluster en fonction du nombre d'articles/mots ?
    if nb_mots>700:
        texte=" ".join(texte.split()[:700]) # ne prend pas en compte les mots après le 700e
    
    try :
        summary=summarizer(texte, max_length=max_length, min_length=min_length)
        return summary[0]["summary_text"]
    except Exception as e:
        print(f"Erreur lors de la génération du résumé : {e}")
        return "Erreur lors de la génération du résumé."

def global_summary(resume_themes):
    print("Résumé global en cours")
    texte=". ".join(resume_themes.values())
    print(f"Texte à résumer : {texte}")
    nb_mots=len(texte.split())
    #print(f"Nombre de mots : {nb_mots}")
    if nb_mots<100:
        max_mots=nb_mots//2
    elif nb_mots<250:
        max_mots=nb_mots//4
    else:
        max_mots=nb_mots//10

    if max_mots<50 and max_mots>=10:
        min_mots=10
    elif max_mots<10:
        summary="Texte trop court pour générer un résumé pertinent.\n"
        summary+=texte
        return summary
    else :
        min_mots=50

    summary=generer_summary(texte, summarizer, max_mots, min_mots)
    return summary

def themes_summary(dataframe):
    print("Résumé par thème en cours")
    summaries={}
    for cluster in sorted(dataframe["cluster"].unique()):
        print(f"Traitement du cluster {cluster} en cours")
        print(f"Nombre d'article : {len(dataframe[dataframe['cluster']==cluster])}")
        titres=dataframe[dataframe["cluster"]==cluster]["titres"].tolist()
        texte=". ".join(titres)

        nb_mots=len(texte.split())
        if nb_mots<10:
            max_mots=nb_mots
        else:
            max_mots=nb_mots//2

        if max_mots<10:
            print("Texte trop court")
            summary="Texte trop court pour générer un résumé pertinent.\n"
            summary+=texte
            return summary
        else :
            min_mots=10
        print("Nb mots : ", nb_mots, "- max mots : ", max_mots, "- min mots : ", min_mots)
        summary=generer_summary(texte, summarizer, max_mots, min_mots)
        summaries[cluster]=summary
        print(summary)
        print("--------")
    return summaries


def recuperation_infos_chercheur(nom, user, mdp, n_clusters=5):
    # recupération des articles pour le chercheur
    token=get_token(user, mdp)
    infos=get_infos_chercheur(nom, token)
    if not infos:
        return {"error": "Aucune info trouvée pour ce chercheur."}

    # extraction des titres des articles
    titres=[]
    taille=[]
    for pub in infos["publications"]:
        # print(pub["titre"])
        titres.append(pub["titre"])
        taille.append(len(pub["titre"]))
    print(f"{len(titres)} titres récupérés pour {nom}.")
    print(f"Taille moyenne des titres : {sum(taille)/len(taille):.2f} caractères.")

    # génération des embeddings
    embeddings=generer_embeddings(titres)

    # génération des clusters
    labels=cluster_embeddings(embeddings, n_clusters=n_clusters)

    titres_labels=pd.DataFrame({"titres": titres, "cluster": labels})
    for cluster in sorted(titres_labels["cluster"].unique()):
        print(f"Cluster {cluster} : ")
        titles_in_cluster=titres_labels[titres_labels["cluster"]==cluster]["titres"].to_list()
        for t in titles_in_cluster:
            print("-", t)
        print("--------")

    # création des résumés
    resume_themes=themes_summary(titres_labels)
    resume_global=global_summary(resume_themes)

    print(f"Résumé global de {nom} : {resume_global}")
    print("------")
    #print(f"Résumés par thématiques : {resume_themes}")  

