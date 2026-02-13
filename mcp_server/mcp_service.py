import sys
import os
from typing import Dict, List, Optional, Any
import streamlit as st
import requests

# Add parent directory to path to import MCP modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server.researchMCPServer import ResearchMCPServer
from mcp_server.researchClient_groq import GroqLLMClient


class MCPServiceManager:
    """
    Gestionnaire du service MCP pour Streamlit
    Initialise et gère l'interaction avec le serveur MCP et le client LLM Groq
    """

    def __init__(self, api_base_url: str = None, api_token: str = None):
        """
        Initialiser le gestionnaire MCP

        Args:
            api_base_url: URL de base de l'API (par défaut: depuis env ou http://api:8000)
            api_token: Token JWT pour authentification API (par défaut: depuis session)
        """
        self.api_base_url = api_base_url or os.getenv("API_BASE_URL", "http://api:8000")
        self.api_token    = api_token
        self.mcp_server   = None
        self.groq_client  = None
        self._initialize()

    def _initialize(self):
        """Initialiser le serveur MCP et le client Groq"""
        try:
            self.mcp_server = ResearchMCPServer(
                api_base_url=self.api_base_url,
                api_token=self.api_token
            )

            groq_api_key = os.environ.get("GROQ_API_KEY")
            if not groq_api_key:
                raise ValueError("GROQ_API_KEY n'est pas défini dans les variables d'environnement")

            self.groq_client = GroqLLMClient(self.mcp_server, api_key=groq_api_key)

        except Exception as e:
            st.error(f"Erreur lors de l'initialisation du service MCP: {str(e)}")
            raise

    # ============= CHAT =============

    def query(self, user_message: str) -> str:
        """
        Traiter une question utilisateur via le client MCP Groq

        Args:
            user_message: La question de l'utilisateur

        Returns:
            Réponse formatée du serveur MCP
        """
        if not self.groq_client:
            return "Erreur: Client Groq non initialisé"

        try:
            return self.groq_client.chat(user_message)
        except Exception as e:
            return f"Erreur lors du traitement de la question: {str(e)}"

    # ============= ACCÈS DIRECT AUX OUTILS MCP =============

    def get_global_stats(self) -> Dict:
        """Obtenir les statistiques globales de la base de données"""
        if not self.mcp_server:
            return {"error": "Serveur MCP non initialisé"}
        return self.mcp_server.get_global_stats()

    def get_top_chercheurs(self, limit: int = 10) -> List[Dict]:
        """Obtenir le classement des chercheurs par nombre de publications"""
        if not self.mcp_server:
            return {"error": "Serveur MCP non initialisé"}
        return self.mcp_server.get_top_chercheurs(limit)

    def get_top_collaborations(self, limit: int = 10) -> List[Dict]:
        """Obtenir les collaborations les plus fortes"""
        if not self.mcp_server:
            return {"error": "Serveur MCP non initialisé"}
        return self.mcp_server.get_top_collaborations(limit)

    def get_stats_pays(self, pays: str = None) -> List[Dict]:
        """Obtenir les statistiques de publications par pays"""
        if not self.mcp_server:
            return {"error": "Serveur MCP non initialisé"}
        return self.mcp_server.get_stats_pays(pays)

    def find_potential_collaborators(self, nom: str, limit: int = 10) -> Dict:
        """Suggérer des collaborateurs potentiels pour un chercheur"""
        if not self.mcp_server:
            return {"error": "Serveur MCP non initialisé"}
        return self.mcp_server.find_potential_collaborators(nom, limit)

    def get_collaboration_network(self, nom: str) -> Dict:
        """Obtenir le réseau de collaboration centré sur un chercheur"""
        if not self.mcp_server:
            return {"error": "Serveur MCP non initialisé"}
        return self.mcp_server.get_collaboration_network(nom)

    def list_tools(self) -> List[Dict]:
        """Obtenir la liste de tous les outils MCP disponibles"""
        if not self.mcp_server:
            return [{"error": "Serveur MCP non initialisé"}]
        return self.mcp_server.get_tools_schema()

    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Exécuter un outil MCP par son nom"""
        if not self.mcp_server:
            return {"error": "Serveur MCP non initialisé"}
        return self.mcp_server.execute_tool(tool_name, **kwargs)


# ============= HELPERS STREAMLIT =============

def get_mcp_manager() -> MCPServiceManager:
    """
    Obtenir une instance du gestionnaire MCP mise en cache dans la session Streamlit.
    Utilise le token de session si disponible.
    """
    api_token    = st.session_state.get("api_token", None)
    api_base_url = os.getenv("API_BASE_URL", "http://api:8000")

    # Clé de cache unique par token pour éviter les collisions entre utilisateurs
    cache_key = f"mcp_manager_{api_token}"

    if cache_key not in st.session_state:
        st.session_state[cache_key] = MCPServiceManager(
            api_base_url=api_base_url,
            api_token=api_token
        )

    return st.session_state[cache_key]


def initialize_mcp_session_state():
    """Initialiser l'état de session Streamlit pour le chat MCP"""
    if "mcp_messages" not in st.session_state:
        st.session_state.mcp_messages = []

    if "mcp_initialized" not in st.session_state:
        st.session_state.mcp_initialized = False


def add_mcp_message(role: str, content: str):
    """Ajouter un message à l'historique du chat"""
    st.session_state.mcp_messages.append({
        "role":    role,
        "content": content
    })


def get_mcp_messages() -> List[Dict]:
    """Obtenir l'historique des messages"""
    return st.session_state.mcp_messages


def clear_mcp_messages():
    """Effacer l'historique du chat"""
    st.session_state.mcp_messages = []