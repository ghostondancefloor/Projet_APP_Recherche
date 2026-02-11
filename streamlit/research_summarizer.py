import torch
import pandas as pd
import requests
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from typing import List, Tuple, Dict
from transformers import BartTokenizer, BartForConditionalGeneration, T5Tokenizer, T5ForConditionalGeneration
import os

class ResearchSummarizer:
    def __init__(self, api_url: str, n_clusters: int = 5):
        """
        Initialise les modèles IA au démarrage
        """
        self.api_url = api_url.rstrip('/')
        self.n_clusters = n_clusters
        
        # détection du matériel
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Initialisation sur : {self.device}...", flush=True)

        # chargement des modèles
        self.chargement_model()

    def chargement_model(self):
        print("Chargement des modèles...", flush=True)
        # chemin vers les modèles dans l'image Docker
        base_dir = "/app/models_local"
        path_embed = f"{base_dir}/embedding"
        path_bart = f"{base_dir}/bart"
        path_t5 = f"{base_dir}/t5"

        try:
            # calcul des embedding
            if os.path.exists(path_embed):
                self.embedder = SentenceTransformer(path_embed)
            else:
                print("problème lors du chargement local de l'embedding")

            # chargement du modèle bart
            if os.path.exists(path_bart):
                print(f"-> Chargement Local : {path_bart}")
                source_bart = path_bart
            else:
                print("problème lors du chargement local de BART")


            self.bartTokenizer = BartTokenizer.from_pretrained(source_bart)
            self.bartModel = BartForConditionalGeneration.from_pretrained(source_bart)

            # chargement du modèle t5
            if os.path.exists(path_t5):
                print(f"-> Chargement Local : {path_t5}")
                source_t5 = path_t5
            else:
                print("problème lors du chargement local de T5")

            self.t5Tokenizer = T5Tokenizer.from_pretrained(source_t5)
            self.t5Model = T5ForConditionalGeneration.from_pretrained(source_t5)
    
            # Déplacement sur GPU si disponible
            self.bartModel.to(self.device)
            self.t5Model.to(self.device)
            print("Modèles IA chargés avec succès.")

        except Exception as e:
            print(f"Erreur lors du chargement des modèles : {e}")
            raise e

    def recuperation_titres(self, researcher_name: str, token: str) -> List[str]:
        headers = {"Authorization": f"Bearer {token}"}
        try:
            print(f"Recherche API pour : {researcher_name}")
            r = requests.get(f"{self.api_url}/api/chercheurs/{researcher_name}", headers=headers)
            
            if r.status_code == 401:
                print("Erreur : Token invalide.")
                return []
            if r.status_code != 200:
                print(f"Erreur API ({r.status_code}): {r.text}")
                return []
                
            data = r.json()
            # Sécurité si la clé 'publications' est absente
            pubs = data.get("publications", [])
            titres = [p["titre"] for p in pubs if "titre" in p]
            return titres
            
        except Exception as e:
            print(f"Erreur réseau : {e}")
            return []

    def creation_clusters(self, titles: List[str]) -> pd.DataFrame:
        if not titles: 
            return pd.DataFrame()
            
        # vectorisation des embeddings
        embeddings = self.embedder.encode(titles, show_progress_bar=False)
        
        # adaptation du nombre de clusters en fonction du nombre d'articles
        #k = min(self.n_clusters, len(titles))
        k = max(3, min(8, len(titles) // 15))
        if k < 2:
            labels = [0] * len(titles)
        else:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(embeddings)
            
        return pd.DataFrame({"titre": titles, "cluster": labels})

    def generer_synthese(self, text_list: List[str], max_len: int, min_len: int) -> List[str]:
        if not text_list:
            return []

        # tokenisation : transformer le texte en chiffres
        inputs = self.bartTokenizer(
            text_list, 
            max_length=1024, 
            return_tensors="pt", 
            truncation=True, 
            padding=True
        )

        # utilisation du GPU si disponible
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # génération du résumé

        # paramétrage du modèle
        summary_ids = self.bartModel.generate(
            inputs["input_ids"], 
            num_beams=2, 
            max_length=max_len, 
            min_length=min_len,
            no_repeat_ngram_size=3, #pour éviter les répétitions
            repetition_penalty=2.5, # pour éviter de redire la même chose
            length_penalty=2.0, 
            early_stopping=True
        )

        # décode le résumé
        decoded_texts = self.bartTokenizer.batch_decode(summary_ids, skip_special_tokens=True)
        return decoded_texts
    
    def generer_resume(self, content:str, prompt:str) -> str:      
      
        prompt = (f"{prompt} : {content}")

        inputs=self.t5Tokenizer(
            prompt,
            return_tensors="pt",
            max_length=1024,
            truncation=True
        ).to(self.device)

        summary_ids = self.t5Model.generate(
            inputs["input_ids"],
            do_sample=False, # On repasse en déterministe pour éviter les coupures de mots
            num_beams=4,
            max_length=150,
            min_length=40,
            no_repeat_ngram_size=3,
            repetition_penalty=5.0,
            early_stopping=True
        )
        
            
        return self.t5Tokenizer.decode(summary_ids[0], skip_special_tokens=True)
   
    
    def generer_presentation_bart(self, df: pd.DataFrame) -> Tuple[Dict[int, str], str]:
        cluster_texts = []
        cluster_ids = []
        MAX_CHAR = 3000 # Sécurité anti-crash

        for cid in sorted(df["cluster"].unique()):
            titles = df[df["cluster"] == cid]["titre"].tolist()
            # concaténation propre
            text = ". ".join([t.strip().rstrip('.') for t in titles]) + "."
            
            # troncature de sécurité pour éviter les dépassements
            if len(text) > MAX_CHAR:
                text = text[:MAX_CHAR].rsplit(' ', 1)[0] + "."
                
            cluster_texts.append(text)
            cluster_ids.append(cid)

        print(f"Génération des résumés pour {len(cluster_texts)} thèmes...", flush=True)

        try:
            summaries_list = self.generer_synthese(
                cluster_texts, 
                max_len=100, 
                min_len=20
            )
        except Exception as e:
            return {}, f"Erreur IA : {str(e)}"

        # association des résumés aux identifiants des clusters
        themes = {}
        for cid, txt in zip(cluster_ids, summaries_list):
            themes[cid] = self.generer_resume(txt, prompt="Rewrite as a natural sentence")

        return themes
    

    def creer_presentation(self, researcher_name: str, token: str):
        print(f"Analyse lancée pour : {researcher_name}")
        
        # récupération des titres
        titles = self.recuperation_titres(researcher_name, token)
        if not titles:
            return None # Ou lever une erreur selon ton besoin
        print(f"{len(titles)} articles récupérés.")

        # création des clusters
        df = self.creation_clusters(titles)

        # création du résumé
        themes = self.generer_presentation_bart(df)

        # titre
        if isinstance(themes, tuple):
            titre="Erreur lors de la génération"

        else:
            try:
                text_for_title = " ".join(themes.values())
                start="This researcher has worked on : "
                titre = start + self.generer_resume(text_for_title, prompt="Generate a concise and catchy title for a research summary based on the following themes")

            except Exception as e:
                print(f"Erreur lors de la génération du résumé : {e}")
                titre=f"Erreur lors de la génération du titre : {e}"
        return {
            "name": researcher_name,
            "article_count": len(titles),
            "global_summary": titre,
            "themes": themes
        }