import requests
from typing import Any, Dict, List, Optional
import os

# ============================================================================
# SERVEUR MCP - Gestion de la base de données de recherche
# ============================================================================

class ResearchMCPServer:
    """
    Serveur MCP pour gérer une base de données de recherche académique

    RÔLE DU SERVEUR MCP:
    1. TRADUCTEUR: Convertit les demandes → requêtes sur les données
    2. SÉCURITÉ: Contrôle les accès et valide les données
    3. ORCHESTRATEUR: Combine plusieurs sources de données
    """

    def __init__(self, api_base_url: str = None, api_token: str = None):
        """
        Initialiser le serveur MCP avec accès à l'API

        Args:
            api_base_url: URL de base de l'API (ex: http://api:8000)
            api_token: Token JWT pour l'authentification
        """
        self.api_base_url = api_base_url or os.getenv("API_BASE_URL", "http://api:8000")
        self.api_token    = api_token    or os.getenv("API_TOKEN", "")

        # Cache des données pour réduire les appels API
        self.chercheurs     = []
        self.publications   = []
        self.institutions   = []
        self.collaborations = []
        self.stats_pays     = []

        self._load_data()

    # ============= CONNEXION API =============

    def _get_headers(self) -> Dict:
        """Retourner les headers avec le token d'authentification"""
        headers = {"Content-Type": "application/json"}
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
        return headers

    def _api_call(self, endpoint: str) -> List[Dict]:
        """
        Faire un appel API et retourner les données

        Args:
            endpoint: L'endpoint de l'API (ex: /api/chercheurs)

        Returns:
            Liste des données ou liste vide en cas d'erreur
        """
        try:
            url = f"{self.api_base_url}{endpoint}"
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Erreur lors de l'appel API {endpoint}: {str(e)}")
            return []

    def _load_data(self):
        """Charger les données depuis l'API"""
        self.chercheurs     = self._api_call("/api/chercheurs")
        self.publications   = self._api_call("/api/publications")
        self.institutions   = self._api_call("/api/institutions")
        self.collaborations = self._api_call("/api/collaborations")
        self.stats_pays     = self._api_call("/api/stats_pays")

    # ============= OUTILS MCP =============

    def get_global_stats(self) -> Dict:
        """Statistiques globales de la base de données"""
        return {
            "total_chercheurs":     len(self.chercheurs),
            "total_publications":   len(self.publications),
            "total_institutions":   len(self.institutions),
            "total_collaborations": len(self.collaborations),
            "nb_pays":              len(set(s.get("pays") for s in self.stats_pays))
        }

    def get_top_chercheurs(self, limit: int = 10) -> List[Dict]:
        """Top chercheurs par nombre de publications"""
        sorted_chercheurs = sorted(
            self.chercheurs,
            key=lambda x: len(x.get("publications", [])),
            reverse=True
        )[:limit]

        return [
            {
                "nom": c.get("nom"),
                "nb_publications": len(c.get("publications", [])),
                "total_citations": sum(
                    p.get("citations", 0)
                    for p in c.get("publications", [])
                    if isinstance(p.get("citations"), int)
                )
            }
            for c in sorted_chercheurs
        ]

    def get_top_collaborations(self, limit: int = 10) -> List[Dict]:
        """Collaborations les plus fortes"""
        sorted_collabs = sorted(
            self.collaborations,
            key=lambda x: x.get("poids", 0),
            reverse=True
        )[:limit]

        return [
            {
                "chercheur1": c.get("chercheur1"),
                "chercheur2": c.get("chercheur2"),
                "poids":      c.get("poids", 0)
            }
            for c in sorted_collabs
        ]

    def get_stats_pays(self, pays: str = None) -> List[Dict]:
        """Statistiques par pays"""
        if pays:
            pays_lower = pays.lower()
            results = [
                {
                    "pays":               s.get("pays"),
                    "annee":              s.get("annee"),
                    "nombre_publications": s.get("nombre_publications", 0)
                }
                for s in self.stats_pays
                if pays_lower in s.get("pays", "").lower()
            ]
            return results if results else {"error": f"Aucune statistique pour '{pays}'"}

        pays_dict = {}
        for s in self.stats_pays:
            p = s.get("pays", "Inconnu")
            if p not in pays_dict:
                pays_dict[p] = 0
            pays_dict[p] += s.get("nombre_publications", 0)

        return sorted(
            [{"pays": k, "total_publications": v} for k, v in pays_dict.items()],
            key=lambda x: x["total_publications"],
            reverse=True
        )[:20]

    def find_potential_collaborators(self, nom: str, limit: int = 10) -> Dict:
        """
        Suggère des collaborateurs potentiels pour un chercheur donné.

        Stratégie de scoring (sur 100) :
        - Collaborateurs de collaborateurs (réseau degré 2) : +40 pts max
        - Thématiques communes dans les titres de publications : +40 pts max
        - Même institution                                    : +20 pts
        Les collaborateurs déjà existants sont exclus du résultat final.
        """
        if not nom:
            return {"error": "Le nom est requis"}

        nom_lower         = nom.lower()
        chercheur_source  = None
        for c in self.chercheurs:
            if nom_lower in c.get("nom", "").lower():
                chercheur_source = c
                break

        if not chercheur_source:
            return {"error": f"Aucun chercheur trouvé avec '{nom}'"}

        collabs_directs = set(chercheur_source.get("collaborateurs", []))
        instits_source  = set(chercheur_source.get("institutions", []))
        publis_source   = chercheur_source.get("publications", [])

        # Extraire les mots-clés thématiques des titres (mots > 4 lettres, hors stopwords)
        stopwords = {
            "dans", "avec", "pour", "vers", "entre", "selon", "from", "with",
            "using", "based", "learning", "deep", "neural", "network", "approach",
            "analysis", "study", "model", "system", "data", "method"
        }

        def extract_keywords(publications: List) -> set:
            keywords = set()
            for p in publications:
                titre = p.get("titre", "") if isinstance(p, dict) else ""
                for word in titre.lower().split():
                    clean = word.strip(".,():;\"'")
                    if len(clean) > 4 and clean not in stopwords:
                        keywords.add(clean)
            return keywords

        keywords_source = extract_keywords(publis_source)

        # --- Scorer chaque chercheur du labo ---
        candidats = []

        for c in self.chercheurs:
            cnom = c.get("nom", "")

            # Exclure le chercheur lui-même et ses collaborateurs directs
            if nom_lower in cnom.lower():
                continue
            if cnom in collabs_directs:
                continue

            score   = 0
            raisons = []

            # Critère 1 : réseau de degré 2 (collaborateurs de collaborateurs)
            collabs_candidat = set(c.get("collaborateurs", []))
            amis_communs     = collabs_directs & collabs_candidat
            if amis_communs:
                pts    = min(len(amis_communs) * 8, 40)
                score += pts
                raisons.append(
                    f"{len(amis_communs)} collaborateur(s) en commun : "
                    f"{', '.join(list(amis_communs)[:3])}"
                )

            # Critère 2 : thématiques communes
            keywords_candidat = extract_keywords(c.get("publications", []))
            themes_communs    = keywords_source & keywords_candidat
            if themes_communs:
                pts    = min(len(themes_communs) * 4, 40)
                score += pts
                raisons.append(
                    f"{len(themes_communs)} thème(s) commun(s) : "
                    f"{', '.join(list(themes_communs)[:4])}"
                )

            # Critère 3 : même institution
            instits_candidat = set(c.get("institutions", []))
            if instits_source & instits_candidat:
                score += 20
                raisons.append("même institution")

            if score > 0:
                candidats.append({
                    "nom":                 cnom,
                    "score_compatibilite": min(score, 100),
                    "raisons":             raisons,
                    "nb_publications":     len(c.get("publications", [])),
                    "nb_collaborateurs":   len(c.get("collaborateurs", []))
                })

        candidats.sort(key=lambda x: x["score_compatibilite"], reverse=True)

        return {
            "chercheur":              chercheur_source.get("nom"),
            "collaborateurs_actuels": len(collabs_directs),
            "candidats_suggeres":     candidats[:limit],
            "total_candidats_trouves": len(candidats)
        }

    def get_collaboration_network(self, nom: str) -> Dict:
        """
        Retourne le réseau de collaboration centré sur un chercheur.

        Analyse :
        - Connexions directes (degré 1) avec leur force de lien
        - Ponts vers d'autres clusters (connexions de connexions uniques)
        - Chercheurs isolés du labo (aucune collaboration connue)
        - Densité du réseau local
        """
        if not nom:
            return {"error": "Le nom est requis"}

        nom_lower        = nom.lower()
        chercheur_source = None
        for c in self.chercheurs:
            if nom_lower in c.get("nom", "").lower():
                chercheur_source = c
                break

        if not chercheur_source:
            return {"error": f"Aucun chercheur trouvé avec '{nom}'"}

        collabs_directs     = chercheur_source.get("collaborateurs", [])
        collabs_directs_set = set(collabs_directs)

        # --- Force de chaque lien direct (via la table des collaborations) ---
        liens_directs = []
        for collab_nom in collabs_directs:
            poids   = 0
            nom_src = chercheur_source.get("nom", "")
            for collab_entry in self.collaborations:
                c1 = collab_entry.get("chercheur1", "")
                c2 = collab_entry.get("chercheur2", "")
                if (c1 == nom_src and c2 == collab_nom) or \
                   (c2 == nom_src and c1 == collab_nom):
                    poids = collab_entry.get("poids", 0)
                    break

            liens_directs.append({
                "nom":        collab_nom,
                "force_lien": poids,
                "type":       "direct"
            })

        liens_directs.sort(key=lambda x: x["force_lien"], reverse=True)

        # --- Ponts : collaborateurs de collaborateurs NON connectés à la source ---
        ponts = {}
        for collab_nom in collabs_directs:
            for c in self.chercheurs:
                if c.get("nom") == collab_nom:
                    for collab2 in c.get("collaborateurs", []):
                        if collab2 != chercheur_source.get("nom") and \
                           collab2 not in collabs_directs_set:
                            if collab2 not in ponts:
                                ponts[collab2] = []
                            ponts[collab2].append(collab_nom)  # accessible via qui
                    break

        ponts_liste = [
            {
                "nom":             nom_pont,
                "accessible_via":  via[:3],
                "nb_chemins":      len(via)
            }
            for nom_pont, via in ponts.items()
        ]
        ponts_liste.sort(key=lambda x: x["nb_chemins"], reverse=True)

        # --- Chercheurs isolés (aucune collaboration dans le labo) ---
        tous_connectes = collabs_directs_set | {p["nom"] for p in ponts_liste}
        tous_connectes.add(chercheur_source.get("nom", ""))

        isoles = [
            c.get("nom")
            for c in self.chercheurs
            if c.get("nom") not in tous_connectes
            and len(c.get("collaborateurs", [])) == 0
        ]

        # --- Densité du réseau local ---
        # Parmi les connexions directes, combien se connaissent entre elles ?
        liens_internes = 0
        for i, c1_nom in enumerate(collabs_directs):
            for c2_nom in collabs_directs[i + 1:]:
                for c in self.chercheurs:
                    if c.get("nom") == c1_nom:
                        if c2_nom in c.get("collaborateurs", []):
                            liens_internes += 1
                        break

        nb_collabs      = len(collabs_directs)
        liens_possibles = (nb_collabs * (nb_collabs - 1)) // 2 if nb_collabs > 1 else 1
        densite         = round((liens_internes / liens_possibles) * 100, 1) if liens_possibles > 0 else 0

        return {
            "chercheur": chercheur_source.get("nom"),
            "resume": {
                "nb_connexions_directes":         len(collabs_directs),
                "nb_ponts_vers_autres_clusters":  len(ponts_liste),
                "nb_chercheurs_isoles_du_reseau": len(isoles),
                "densite_reseau_local":           f"{densite}%"
            },
            "connexions_directes":          liens_directs[:15],
            "ponts_vers_autres_clusters":   ponts_liste[:10],
            "chercheurs_isoles":            isoles[:10],
            "opportunites": (
                f"Vous pouvez atteindre {len(ponts_liste)} chercheur(s) supplémentaire(s) "
                f"via votre réseau actuel. "
                + (
                    f"{len(isoles)} chercheur(s) du labo ne sont connectés à personne — "
                    f"opportunités de nouvelles collaborations."
                    if isoles else ""
                )
            )
        }

    # ============= GESTIONNAIRE D'OUTILS MCP =============

    def get_tools_schema(self) -> List[Dict]:
        """Retourne le schéma des outils pour le LLM"""
        return [
            {
                "name": "get_global_stats",
                "description": "Obtenir les statistiques globales de la base de données "
                               "(nombre total de chercheurs, publications, institutions, etc.)",
                "parameters": {}
            },
            {
                "name": "get_top_chercheurs",
                "description": "Obtenir le classement des chercheurs avec le plus de publications "
                               "dans la base de données",
                "parameters": {"limit": "integer - nombre de chercheurs à retourner (défaut: 10)"}
            },
            {
                "name": "get_top_collaborations",
                "description": "Obtenir les collaborations les plus fortes d'après la base de données",
                "parameters": {"limit": "integer - nombre (défaut: 10)"}
            },
            {
                "name": "get_stats_pays",
                "description": "Obtenir les statistiques de publications par pays d'après la base de données",
                "parameters": {"pays": "string - nom du pays (optionnel, si vide retourne tous les pays)"}
            },
            {
                "name": "find_potential_collaborators",
                "description": "Suggérer des collaborateurs potentiels pour un chercheur, basé sur "
                               "les thématiques communes, le réseau de degré 2 et les institutions partagées",
                "parameters": {
                    "nom":   "string - nom du chercheur",
                    "limit": "integer - nombre de suggestions (défaut: 10)"
                }
            },
            {
                "name": "get_collaboration_network",
                "description": "Visualiser le réseau de collaboration d'un chercheur : connexions directes, "
                               "ponts vers d'autres clusters, chercheurs isolés et densité du réseau local",
                "parameters": {"nom": "string - nom du chercheur"}
            },
        ]

    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Exécuter un outil MCP par son nom"""
        tools = {
            "get_global_stats":             self.get_global_stats,
            "get_top_chercheurs":           self.get_top_chercheurs,
            "get_top_collaborations":       self.get_top_collaborations,
            "get_stats_pays":               self.get_stats_pays,
            "find_potential_collaborators": self.find_potential_collaborators,
            "get_collaboration_network":    self.get_collaboration_network,
        }

        if tool_name not in tools:
            return {"error": f"Outil '{tool_name}' non trouvé"}

        try:
            filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None and v != ""}
            return tools[tool_name](**filtered_kwargs)
        except Exception as e:
            return {"error": f"Erreur: {str(e)}"}