from .researchMCPServer import ResearchMCPServer
from groq import Groq
import json
import os
from typing import Any, Dict, List, Optional

# ============================================================================
# CLIENT LLM GROQ - Utilise Groq API pour interpréter et répondre
# ============================================================================

class GroqLLMClient:
    """
    Client LLM qui utilise Groq API pour interpréter les questions
    et appeler les outils MCP appropriés
    """

    def __init__(self, mcp_server: ResearchMCPServer, api_key: str = None, model: str = "llama-3.3-70b-versatile"):
        self.mcp   = mcp_server
        self.model = model
        self.conversation_history = []

        self.client = Groq(api_key=api_key or os.environ.get("GROQ_API_KEY"))
        self.system_prompt = self._build_system_prompt()

    # ============= CONSTRUCTION DU PROMPT SYSTÈME =============

    def _build_system_prompt(self) -> str:
        """Construire le prompt système avec la description des outils"""
        tools = self.mcp.get_tools_schema()
        tools_description = "\n".join([
            f"- {t['name']}: {t['description']}"
            for t in tools
        ])

        return f"""Tu es un assistant qui DOIT utiliser les outils MCP pour répondre aux questions sur la base de données de recherche.

RÈGLE ABSOLUE: Tu n'as AUCUNE connaissance sur les chercheurs, publications ou institutions. Tu DOIS OBLIGATOIREMENT appeler un outil pour CHAQUE question.

OUTILS DISPONIBLES:
{tools_description}

FORMAT DE RÉPONSE OBLIGATOIRE:
Pour TOUTE question sur les données, réponds UNIQUEMENT avec ce JSON (rien d'autre):
{{"tool": "nom_outil", "params": {{"param": "valeur"}}}}

MAPPING DES QUESTIONS → OUTILS:
- "statistiques" / "stats globales" / "combien"           → {{"tool": "get_global_stats", "params": {{}}}}
- "top chercheurs" / "meilleurs chercheurs"               → {{"tool": "get_top_chercheurs", "params": {{"limit": 10}}}}
- "top collaborations" / "collaborations les plus fortes" → {{"tool": "get_top_collaborations", "params": {{"limit": 10}}}}
- "stats pays X" / "France" / "Canada"                   → {{"tool": "get_stats_pays", "params": {{"pays": "X"}}}}
- "collaborateurs potentiels pour X" / "avec qui X"      → {{"tool": "find_potential_collaborators", "params": {{"nom": "X"}}}}
- "réseau de X" / "réseau collaboration X"               → {{"tool": "get_collaboration_network", "params": {{"nom": "X"}}}}

INTERDIT:
- Ne réponds JAMAIS avec tes propres connaissances
- Ne dis JAMAIS "je ne sais pas" sans appeler un outil d'abord
- N'ajoute AUCUN texte avant ou après le JSON
- Réponds que par LES INFORMATIONS OBTENUES via l'outil

SEULE EXCEPTION: Pour "bonjour", "aide", "merci", tu peux répondre normalement."""

    # ============= PARSING ET APPEL LLM =============

    def _parse_tool_call(self, response: str) -> Optional[Dict]:
        """Extraire un appel d'outil de la réponse du LLM"""
        import re

        response = response.strip()

        # Méthode 1: La réponse est directement un JSON valide
        try:
            parsed = json.loads(response)
            if isinstance(parsed, dict) and "tool" in parsed:
                return parsed
        except:
            pass

        # Méthode 2: Chercher un JSON dans la réponse
        try:
            json_patterns = [
                r'\{["\']?tool["\']?\s*:\s*["\'][^"\']+["\'][^}]*\}',
                r'\{"tool":\s*"[^"]+",\s*"params":\s*\{[^}]*\}\}',
                r'\{.*"tool".*"params".*\}'
            ]
            for pattern in json_patterns:
                json_match = re.search(pattern, response, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group())
                    except:
                        continue
        except:
            pass

        # Méthode 3: Chercher les noms d'outils dans le texte
        tool_names = [
            "get_global_stats", "get_top_chercheurs", "get_top_collaborations",
            "get_stats_pays", "find_potential_collaborators", "get_collaboration_network"
        ]

        response_lower = response.lower()
        for tool_name in tool_names:
            if tool_name in response_lower:
                params = {}

                limit_match = re.search(r'limit["\s:]+(\d+)', response)
                if limit_match:
                    params["limit"] = int(limit_match.group(1))

                nom_match = re.search(r'nom["\s:]+["\']([^"\']+)["\']', response)
                if nom_match:
                    params["nom"] = nom_match.group(1)

                pays_match = re.search(r'pays["\s:]+["\']([^"\']+)["\']', response)
                if pays_match:
                    params["pays"] = pays_match.group(1)

                return {"tool": tool_name, "params": params}

        return None

    def _call_llm(self, messages: List[Dict], temperature: float = 0.7) -> str:
        """Appeler le LLM Groq"""
        try:
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=temperature,
                max_tokens=1024,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"Erreur de connexion à Groq API: {str(e)}"

    # ============= FORMATAGE DES RÉSULTATS =============

    def _format_results_as_text(self, tool_name: str, results: Any, user_question: str) -> str:
        """Formater les résultats de manière lisible si le LLM échoue"""

        if isinstance(results, dict) and "error" in results:
            return f"❌ {results['error']}"

        if tool_name == "get_global_stats":
            return (
                f"📊 **Statistiques globales de la base de données :**\n\n"
                f"- 👨‍🔬 **Chercheurs:** {results.get('total_chercheurs', 0)}\n"
                f"- 📄 **Publications:** {results.get('total_publications', 0)}\n"
                f"- 🏛️ **Institutions:** {results.get('total_institutions', 0)}\n"
                f"- 🤝 **Collaborations:** {results.get('total_collaborations', 0)}\n"
                f"- 🌍 **Pays:** {results.get('nb_pays', 0)}\n"
            )

        elif tool_name == "get_top_chercheurs" and isinstance(results, list):
            lines = ["🏆 **Top chercheurs par publications :**\n"]
            for i, c in enumerate(results, 1):
                lines.append(
                    f"{i}. **{c.get('nom', 'N/A')}** — "
                    f"{c.get('nb_publications', 0)} publications, "
                    f"{c.get('total_citations', 0)} citations"
                )
            return '\n'.join(lines)

        elif tool_name == "get_top_collaborations" and isinstance(results, list):
            lines = ["🤝 **Collaborations les plus fortes :**\n"]
            for i, c in enumerate(results, 1):
                lines.append(
                    f"{i}. **{c.get('chercheur1', 'N/A')}** ↔️ **{c.get('chercheur2', 'N/A')}** "
                    f"(poids: {c.get('poids', 0)})"
                )
            return '\n'.join(lines)

        elif tool_name == "get_stats_pays" and isinstance(results, list):
            lines = ["🌍 **Statistiques par pays :**\n"]
            for r in results[:15]:
                if 'total_publications' in r:
                    lines.append(f"- **{r.get('pays', 'N/A')}**: {r.get('total_publications', 0)} publications")
                else:
                    lines.append(
                        f"- {r.get('pays', 'N/A')} ({r.get('annee', 'N/A')}): "
                        f"{r.get('nombre_publications', 0)} publications"
                    )
            return '\n'.join(lines)

        elif tool_name == "find_potential_collaborators" and isinstance(results, dict):
            candidats = results.get("candidats_suggeres", [])
            lines = [
                f"🔍 **Collaborateurs potentiels pour {results.get('chercheur', 'N/A')} :**\n",
                f"_(réseau actuel : {results.get('collaborateurs_actuels', 0)} collaborateurs — "
                f"{results.get('total_candidats_trouves', 0)} candidats analysés)_\n"
            ]
            for i, c in enumerate(candidats, 1):
                lines.append(
                    f"{i}. **{c.get('nom', 'N/A')}** — "
                    f"score : **{c.get('score_compatibilite', 0)}/100**"
                )
                for raison in c.get("raisons", []):
                    lines.append(f"   • {raison}")
                lines.append("")
            return '\n'.join(lines)

        elif tool_name == "get_collaboration_network" and isinstance(results, dict):
            resume = results.get("resume", {})
            lines = [
                f"🕸️ **Réseau de collaboration — {results.get('chercheur', 'N/A')} :**\n",
                f"- 🔗 Connexions directes : **{resume.get('nb_connexions_directes', 0)}**",
                f"- 🌉 Ponts vers d'autres clusters : **{resume.get('nb_ponts_vers_autres_clusters', 0)}**",
                f"- 🏝️ Chercheurs isolés dans le labo : **{resume.get('nb_chercheurs_isoles_du_reseau', 0)}**",
                f"- 📐 Densité du réseau local : **{resume.get('densite_reseau_local', 'N/A')}**\n",
            ]

            connexions = results.get("connexions_directes", [])
            if connexions:
                lines.append("**🔗 Connexions directes (par force de lien) :**")
                for c in connexions[:8]:
                    lines.append(f"  - {c.get('nom', 'N/A')} (force: {c.get('force_lien', 0)})")

            ponts = results.get("ponts_vers_autres_clusters", [])
            if ponts:
                lines.append("\n**🌉 Ponts vers d'autres clusters :**")
                for p in ponts[:5]:
                    via = ', '.join(p.get('accessible_via', []))
                    lines.append(f"  - {p.get('nom', 'N/A')} — via : {via}")

            isoles = results.get("chercheurs_isoles", [])
            if isoles:
                lines.append(f"\n**🏝️ Chercheurs isolés :** {', '.join(isoles[:5])}")

            opportunites = results.get("opportunites", "")
            if opportunites:
                lines.append(f"\n💡 {opportunites}")

            return '\n'.join(lines)

        # Fallback JSON formaté
        return f"**Résultats :**\n```json\n{json.dumps(results, ensure_ascii=False, indent=2)[:2000]}\n```"

    # ============= DÉTECTION AUTOMATIQUE DE L'OUTIL =============

    def _detect_tool_from_question(self, question: str) -> Optional[Dict]:
        """Détecter automatiquement l'outil à utiliser basé sur la question"""
        import re
        q = question.lower().strip()

        # Salutations — pas d'outil
        if any(word in q for word in ["bonjour", "salut", "hello", "merci", "aide", "help"]):
            return None

        # Stats globales
        if ("statistique" in q or "stats" in q or "combien" in q) and \
           ("global" in q or "total" in q or "base" in q or "tout" in q):
            return {"tool": "get_global_stats", "params": {}}

        # Top chercheurs
        if ("top" in q or "meilleurs" in q) and ("chercheur" in q or "auteur" in q):
            limit = next((int(w) for w in q.split() if w.isdigit()), 10)
            return {"tool": "get_top_chercheurs", "params": {"limit": limit}}

        # Top collaborations (sans confondre avec réseau/potentiel)
        if ("top" in q or "plus fortes" in q or "meilleures" in q) and "collaboration" in q \
           and "réseau" not in q and "potentiel" not in q:
            limit = next((int(w) for w in q.split() if w.isdigit()), 10)
            return {"tool": "get_top_collaborations", "params": {"limit": limit}}

        # Stats pays
        countries = {
            "france": "France", "canada": "Canada", "suisse": "Switzerland",
            "belgique": "Belgium", "allemagne": "Germany", "italie": "Italy",
            "espagne": "Spain", "chine": "China", "japon": "Japan", "usa": "USA"
        }
        for key, value in countries.items():
            if key in q:
                return {"tool": "get_stats_pays", "params": {"pays": value}}

        if "pays" in q and ("stats" in q or "statistique" in q or "publication" in q):
            return {"tool": "get_stats_pays", "params": {}}

        # Réseau de collaboration d'un chercheur
        if ("réseau" in q or "network" in q) and ("collaboration" in q or "chercheur" in q):
            words = question.split()
            name_parts = [
                w for w in words
                if w and w[0].isupper() and len(w) > 1
                and w.lower() not in ["réseau", "collaboration", "chercheur"]
            ]
            if name_parts:
                return {"tool": "get_collaboration_network", "params": {"nom": " ".join(name_parts)}}

        # Collaborateurs potentiels
        if "potentiel" in q or "suggér" in q or ("avec qui" in q and "collaborer" in q):
            words = question.split()
            name_parts = [
                w for w in words
                if w and w[0].isupper() and len(w) > 1
                and w.lower() not in ["avec", "qui", "collaborer", "potentiel"]
            ]
            if name_parts:
                return {"tool": "find_potential_collaborators", "params": {"nom": " ".join(name_parts)}}

        # Recherche générique par nom propre
        words = question.split()
        name_parts = [
            w for w in words
            if w and w[0].isupper() and len(w) > 2
            and w.lower() not in ["qui", "est", "que", "quoi", "comment", "pourquoi"]
        ]
        if name_parts:
            nom = " ".join(name_parts)
            if "réseau" in q or "connecté" in q:
                return {"tool": "get_collaboration_network", "params": {"nom": nom}}
            if "collaboration" in q or "collaborer" in q or "potentiel" in q:
                return {"tool": "find_potential_collaborators", "params": {"nom": nom}}

        # Défaut : stats globales
        return {"tool": "get_global_stats", "params": {}}

    # ============= POINT D'ENTRÉE PRINCIPAL =============

    def chat(self, user_message: str) -> str:
        """Traiter un message utilisateur et retourner une réponse"""

        q_lower = user_message.lower().strip()

        # Salutations
        if any(word in q_lower for word in ["bonjour", "salut", "hello", "hi", "coucou"]):
            stats = self.mcp.get_global_stats()
            return (
                f"👋 **Bonjour !** Je suis votre assistant pour explorer la base de données de recherche.\n\n"
                f"📊 **La base contient :**\n"
                f"- 👨‍🔬 {stats['total_chercheurs']} chercheurs\n"
                f"- 📄 {stats['total_publications']} publications\n"
                f"- 🏛️ {stats['total_institutions']} institutions\n\n"
                f"**Posez-moi vos questions !**"
            )

        # Aide
        if any(word in q_lower for word in ["aide", "help", "comment"]):
            return (
                "🆘 **Voici ce que je peux faire :**\n\n"
                "**📊 Statistiques :**\n"
                "- \"Stats globales\" — Vue d'ensemble de la base\n"
                "- \"Stats France\" — Publications par pays\n\n"
                "**🏆 Classements :**\n"
                "- \"Top chercheurs\" — Chercheurs les plus productifs\n"
                "- \"Top collaborations\" — Paires les plus actives\n\n"
                "**🤝 Réseau & Collaborations :**\n"
                "- \"Collaborateurs potentiels pour Dupont\" — Suggestions personnalisées\n"
                "- \"Réseau de collaboration de Martin\" — Carte du réseau d'un chercheur\n"
            )

        # Étape 1 : détection automatique
        tool_call = self._detect_tool_from_question(user_message)

        # Étape 2 : si pas de détection, demander au LLM
        if tool_call is None:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user",   "content": user_message}
            ]
            llm_response = self._call_llm(messages, temperature=0.1)
            tool_call    = self._parse_tool_call(llm_response)

        # Étape 3 : exécuter l'outil et formater la réponse
        if tool_call:
            tool_name   = tool_call.get("tool", "")
            params      = tool_call.get("params", {})
            tool_result = self.mcp.execute_tool(tool_name, **params)

            final_response = self._format_results_as_text(tool_name, tool_result, user_message)

            # Optionnel : améliorer la présentation via le LLM
            if len(str(tool_result)) < 2000:
                try:
                    result_str = json.dumps(tool_result, ensure_ascii=False, indent=2)
                    followup_messages = [
                        {
                            "role": "system",
                            "content": "Présente ces résultats de manière claire et concise avec des emojis. "
                                       "Ne montre PAS le JSON brut. Sois direct et informatif."
                        },
                        {
                            "role": "user",
                            "content": f"Question: {user_message}\n\nDonnées:\n{result_str}"
                        }
                    ]
                    llm_formatted = self._call_llm(followup_messages, temperature=0.3)
                    if len(llm_formatted) > 50 and not llm_formatted.strip().startswith('{'):
                        final_response = llm_formatted
                except:
                    pass  # Garder le formatage par défaut
        else:
            final_response = (
                "Je n'ai pas compris votre question. Essayez par exemple :\n"
                "- \"Stats globales\"\n"
                "- \"Top collaborations\"\n"
                "- \"Collaborateurs potentiels pour Dupont\"\n"
                "- \"Réseau de collaboration de Martin\""
            )

        # Sauvegarder dans l'historique (fenêtre glissante de 20 messages)
        self.conversation_history.append({"role": "user",      "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": final_response})

        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]

        return final_response

    def clear_history(self):
        """Effacer l'historique de conversation"""
        self.conversation_history = []