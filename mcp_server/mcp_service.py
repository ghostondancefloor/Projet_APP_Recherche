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
        self.api_token = api_token
        self.mcp_server = None
        self.groq_client = None
        self._initialize()
    
    def _initialize(self):
        """Initialiser le serveur MCP et le client Groq"""
        try:
            # Initialiser le serveur MCP avec l'API
            self.mcp_server = ResearchMCPServer(
                api_base_url=self.api_base_url,
                api_token=self.api_token
            )
            
            # Initialiser le client Groq
            groq_api_key = os.environ.get("GROQ_API_KEY")
            if not groq_api_key:
                raise ValueError("GROQ_API_KEY n'est pas défini dans les variables d'environnement")
            
            self.groq_client = GroqLLMClient(self.mcp_server, api_key=groq_api_key)
        
        except Exception as e:
            st.error(f"Erreur lors de l'initialisation du service MCP: {str(e)}")
            raise
    
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
            response = self.groq_client.chat(user_message)
            return response
        except Exception as e:
            return f"Erreur lors du traitement de la question: {str(e)}"
    
    def get_global_stats(self) -> Dict:
        """Obtenir les statistiques globales"""
        if not self.mcp_server:
            return {"error": "Serveur MCP non initialisé"}
        return self.mcp_server.get_global_stats()
    
    def search_chercheur(self, nom: str) -> Dict:
        """Chercher un chercheur"""
        if not self.mcp_server:
            return {"error": "Serveur MCP non initialisé"}
        return self.mcp_server.search_chercheur(nom)
    
    def get_top_chercheurs(self, limit: int = 10) -> List[Dict]:
        """Obtenir les top chercheurs"""
        if not self.mcp_server:
            return {"error": "Serveur MCP non initialisé"}
        return self.mcp_server.get_top_chercheurs(limit)
    
    def get_top_publications(self, limit: int = 10) -> List[Dict]:
        """Obtenir les publications les plus citées"""
        if not self.mcp_server:
            return {"error": "Serveur MCP non initialisé"}
        return self.mcp_server.get_top_publications(limit)
    
    def search_publication(self, titre: str) -> List[Dict]:
        """Chercher une publication"""
        if not self.mcp_server:
            return {"error": "Serveur MCP non initialisé"}
        return self.mcp_server.search_publication(titre)
    
    def list_chercheurs(self, limit: int = 30) -> List[str]:
        """Lister les chercheurs"""
        if not self.mcp_server:
            return {"error": "Serveur MCP non initialisé"}
        return self.mcp_server.list_chercheurs(limit)


def get_mcp_manager():
    """
    Obtenir une instance du gestionnaire MCP
    Utilise le token du session state de Streamlit si disponible
    """
    # Récupérer le token de la session Streamlit
    api_token = st.session_state.get("api_token", None)
    api_base_url = os.getenv("API_BASE_URL", "http://api:8000")
    
    # Créer une clé de cache unique avec le token
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
        "role": role,
        "content": content
    })


def get_mcp_messages() -> List[Dict]:
    """Obtenir l'historique des messages"""
    return st.session_state.mcp_messages


def clear_mcp_messages():
    """Effacer l'historique du chat"""
    st.session_state.mcp_messages = []
