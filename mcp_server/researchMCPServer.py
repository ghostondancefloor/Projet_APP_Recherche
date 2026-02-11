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
        self.api_token = api_token or os.getenv("API_TOKEN", "")
        
        # Cache des données pour réduire les appels API
        self.chercheurs = []
        self.publications = []
        self.institutions = []
        self.collaborations = []
        self.stats_pays = []
        
        self._load_data()
    
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
        self.chercheurs = self._api_call("/api/chercheurs")
        self.publications = self._api_call("/api/publications")
        self.institutions = self._api_call("/api/institutions")
        self.collaborations = self._api_call("/api/collaborations")
        self.stats_pays = self._api_call("/api/stats_pays")
    
    # ============= OUTILS MCP =============
    
    def get_global_stats(self) -> Dict:
        """Statistiques globales de la base de données"""
        
        return {
            "total_chercheurs": len(self.chercheurs),
            "total_publications": len(self.publications),
            "total_institutions": len(self.institutions),
            "total_collaborations": len(self.collaborations),
            "nb_pays": len(set(s.get("pays") for s in self.stats_pays))
        }
    #needs to be fixed
    def search_chercheur(self, nom: str) -> Dict:
        """Chercher un chercheur par son nom"""
        if not nom:
            return {"error": "Le nom est requis"}
        
        nom_lower = nom.lower()
        for c in self.chercheurs:
            if nom_lower in c.get("nom", "").lower():
                publications = c.get("publications", [])
                sorted_publications = sorted(
                    publications, 
                    key=lambda p: p.get("annee", 0), 
                    reverse=True
                )
                
                return {
                    "nom": c.get("nom"),
                    "publications": sorted_publications[:10],
                    "collaborateurs": c.get("collaborateurs", [])[:20],
                    "institutions": c.get("institutions", [])[:10],
                    "total_publications": len(publications),
                    "total_collaborateurs": len(c.get("collaborateurs", [])),
                    "total_institutions": len(c.get("institutions", []))
                }
        
        return {"error": f"Aucun chercheur trouvé avec '{nom}'"}
    
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
                "total_citations": sum(p.get("citations", 0) for p in c.get("publications", []) if isinstance(p.get("citations"), int))
            }
            for c in sorted_chercheurs
        ]
    
    def search_publication(self, titre: str) -> List[Dict]:
        """Chercher une publication par titre"""
        if not titre:
            return {"error": "Le titre est requis"}
        
        titre_lower = titre.lower()
        results = []
        
        for p in self.publications:
            if titre_lower in p.get("titre", "").lower():
                results.append({
                    "titre": p.get("titre"),
                    "auteurs": p.get("auteurs", [])[:5],
                    "annee": p.get("annee"),
                    "citations": p.get("citations", 0),
                    "institutions": p.get("institutions", [])
                })
                if len(results) >= 10:
                    break
        
        return results if results else {"error": f"Aucune publication trouvée avec '{titre}'"}
    
    def get_top_publications(self, limit: int = 10) -> List[Dict]:
        """Publications les plus citées"""
        sorted_pubs = sorted(
            [p for p in self.publications if isinstance(p.get("citations"), int)],
            key=lambda x: x.get("citations", 0),
            reverse=True
        )[:limit]
        
        return [
            {
                "titre": p.get("titre"),
                "auteurs": p.get("auteurs", [])[:3],
                "annee": p.get("annee"),
                "citations": p.get("citations", 0)
            }
            for p in sorted_pubs
        ]
    
    def get_publications_by_year(self, annee: int) -> List[Dict]:
        """Publications d'une année spécifique"""
        results = [
            {
                "titre": p.get("titre"),
                "auteurs": p.get("auteurs", [])[:3]
            }
            for p in self.publications
            if p.get("annee") == annee or str(p.get("annee")) == str(annee)
        ][:30]
        
        return results if results else {"error": f"Aucune publication trouvée pour {annee}"}
    
    def search_institution(self, nom: str) -> Dict:
        """Chercher une institution par nom"""
        if not nom:
            return {"error": "Le nom est requis"}
        
        nom_lower = nom.lower()
        for i in self.institutions:
            if nom_lower in i.get("nom", "").lower():
                return {
                    "nom": i.get("nom"),
                    "pays": i.get("pays"),
                    "type": i.get("type"),
                    "chercheurs": i.get("chercheurs", [])[:15],
                    "publications": i.get("publications", [])[:10],
                    "total_chercheurs": len(i.get("chercheurs", [])),
                    "total_publications": len(i.get("publications", []))
                }
        
        return {"error": f"Aucune institution trouvée avec '{nom}'"}
    
    def get_top_institutions(self, limit: int = 10) -> List[Dict]:
        """Top institutions par nombre de chercheurs"""
        sorted_inst = sorted(
            self.institutions,
            key=lambda x: len(x.get("chercheurs", [])),
            reverse=True
        )[:limit]
        
        return [
            {
                "nom": i.get("nom"),
                "pays": i.get("pays"),
                "nb_chercheurs": len(i.get("chercheurs", [])),
                "nb_publications": len(i.get("publications", []))
            }
            for i in sorted_inst
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
                "poids": c.get("poids", 0)
            }
            for c in sorted_collabs
        ]
    
    def get_stats_pays(self, pays: str = None) -> List[Dict]:
        """Statistiques par pays"""
        if pays:
            pays_lower = pays.lower()
            results = [
                {
                    "pays": s.get("pays"),
                    "annee": s.get("annee"),
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
    
    def list_chercheurs(self, limit: int = 30) -> List[str]:
        """Liste des noms de chercheurs"""
        return [c.get("nom", "") for c in self.chercheurs[:limit]]
    
    # ============= GESTIONNAIRE D'OUTILS MCP =============
    
    def get_tools_schema(self) -> List[Dict]:
        """Retourne le schéma des outils pour le LLM"""
        return [
            {
                "name": "get_global_stats",
                "description": "Obtenir les statistiques globales de la base de données (nombre total de chercheurs, publications, institutions, etc.)",
                "parameters": {}
            },
            {
                "name": "search_chercheur",
                "description": "Rechercher un chercheur par son nom et obtenir ses informations (publications, collaborateurs, institutions) de la base de données",
                "parameters": {"nom": "string - nom du chercheur à rechercher"}
            },
            {
                "name": "get_top_chercheurs",
                "description": "Obtenir le classement des chercheurs avec le plus de publications dans la base de données",
                "parameters": {"limit": "integer - nombre de chercheurs à retourner (défaut: 10)"}
            },
            {
                "name": "search_publication",
                "description": "Rechercher des publications par titre de la base de données",
                "parameters": {"titre": "string - titre ou mots-clés à rechercher"}
            },
            {
                "name": "get_top_publications",
                "description": "Obtenir les publications les plus citées de la base de données",
                "parameters": {"limit": "integer - nombre de publications (défaut: 10)"}
            },
            {
                "name": "get_publications_by_year",
                "description": "Obtenir les publications d'une année spécifique, d'après les informations de la base de données",
                "parameters": {"annee": "integer - année (ex: 2020)"}
            },
            {
                "name": "search_institution",
                "description": "Rechercher une institution par nom de la base de données",
                "parameters": {"nom": "string - nom de l'institution"}
            },
            {
                "name": "get_top_institutions",
                "description": "Obtenir les institutions avec qui les chercheurs collaborent le plus d'après la base de données",
                "parameters": {"limit": "integer - nombre d'institutions (défaut: 10)"}
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
                "name": "list_chercheurs",
                "description": "Lister les noms des chercheurs dans la base",
                "parameters": {"limit": "integer - nombre (défaut: 30)"}
            }
        ]
    
    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Exécuter un outil MCP par son nom"""
        tools = {
            "get_global_stats": self.get_global_stats,
            "search_chercheur": self.search_chercheur,
            "get_top_chercheurs": self.get_top_chercheurs,
            "search_publication": self.search_publication,
            "get_top_publications": self.get_top_publications,
            "get_publications_by_year": self.get_publications_by_year,
            "search_institution": self.search_institution,
            "get_top_institutions": self.get_top_institutions,
            "get_top_collaborations": self.get_top_collaborations,
            "get_stats_pays": self.get_stats_pays,
            "list_chercheurs": self.list_chercheurs
        }
        
        if tool_name not in tools:
            return {"error": f"Outil '{tool_name}' non trouvé"}
        
        try:
            # Filtrer les kwargs vides
            filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None and v != ""}
            return tools[tool_name](**filtered_kwargs)
        except Exception as e:
            return {"error": f"Erreur: {str(e)}"}
