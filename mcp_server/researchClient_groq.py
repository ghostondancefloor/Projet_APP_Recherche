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
        self.mcp = mcp_server
        self.model = model
        self.conversation_history = []
        
        # Initialiser le client Groq
        # L'API key peut être passée en paramètre ou via variable d'environnement
        self.client = Groq(api_key=api_key or os.environ.get("GROQ_API_KEY"))
        
        # Construire le prompt système avec les outils disponibles
        self.system_prompt = self._build_system_prompt()
    
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
- "qui est X" / "chercheur X" / "infos sur X" → {{"tool": "search_chercheur", "params": {{"nom": "X"}}}}
- "top publications" / "plus citées" → {{"tool": "get_top_publications", "params": {{"limit": 10}}}}
- "statistiques" / "stats globales" → {{"tool": "get_global_stats", "params": {{}}}}
- "stats pays X" / "France" / "Canada" → {{"tool": "get_stats_pays", "params": {{"pays": "X"}}}}
- "publications année X" / "en 2020" → {{"tool": "get_publications_by_year", "params": {{"annee": X}}}}
- "institution X" / "université X" → {{"tool": "search_institution", "params": {{"nom": "X"}}}}
- "top institutions" → {{"tool": "get_top_institutions", "params": {{"limit": 10}}}}
- "top collaborations" → {{"tool": "get_top_collaborations", "params": {{"limit": 10}}}}
- "publication sur X" / "article X" → {{"tool": "search_publication", "params": {{"titre": "X"}}}}
- "liste chercheurs" → {{"tool": "list_chercheurs", "params": {{}}}}

INTERDIT:
- Ne réponds JAMAIS avec tes propres connaissances
- Ne dis JAMAIS "je ne sais pas" sans appeler un outil d'abord
- N'ajoute AUCUN texte avant ou après le JSON
- Réponds que par LES INFORMATIONS OBTENUES via l'outil

SEULE EXCEPTION: Pour "bonjour", "aide", "merci", tu peux répondre normalement."""
    
    def _parse_tool_call(self, response: str) -> Optional[Dict]:
        """Extraire un appel d'outil de la réponse du LLM"""
        import re
        
        # Nettoyer la réponse
        response = response.strip()
        
        # Méthode 1: La réponse est directement un JSON
        try:
            parsed = json.loads(response)
            if isinstance(parsed, dict) and "tool" in parsed:
                return parsed
        except:
            pass
        
        # Méthode 2: Chercher un JSON dans la réponse
        try:
            # Pattern plus robuste pour trouver le JSON
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
            "get_global_stats", "search_chercheur", "get_top_chercheurs", "search_publication", "get_top_publications",
            "get_publications_by_year", "search_institution", "get_top_institutions", "get_top_collaborations", "get_stats_pays", "list_chercheurs"
        ]
        
        response_lower = response.lower()
        for tool_name in tool_names:
            if tool_name in response_lower:
                # Essayer d'extraire les paramètres
                params = {}
                
                # Chercher limit
                limit_match = re.search(r'limit["\s:]+(\d+)', response)
                if limit_match:
                    params["limit"] = int(limit_match.group(1))
                
                # Chercher nom
                nom_match = re.search(r'nom["\s:]+["\']([^"\']+)["\']', response)
                if nom_match:
                    params["nom"] = nom_match.group(1)
                
                # Chercher titre
                titre_match = re.search(r'titre["\s:]+["\']([^"\']+)["\']', response)
                if titre_match:
                    params["titre"] = titre_match.group(1)
                
                # Chercher pays
                pays_match = re.search(r'pays["\s:]+["\']([^"\']+)["\']', response)
                if pays_match:
                    params["pays"] = pays_match.group(1)
                
                # Chercher annee
                annee_match = re.search(r'annee["\s:]+(\d{4})', response)
                if annee_match:
                    params["annee"] = int(annee_match.group(1))
                
                # Chercher chercheur
                chercheur_match = re.search(r'chercheur["\s:]+["\']([^"\']+)["\']', response)
                if chercheur_match:
                    params["chercheur"] = chercheur_match.group(1)
                
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
    
    def _format_results_as_text(self, tool_name: str, results: Any, user_question: str) -> str:
        """Formater les résultats de manière lisible si le LLM échoue"""
        
        if isinstance(results, dict) and "error" in results:
            return f"❌ {results['error']}"
        
        # Formatage selon le type d'outil
        if tool_name == "get_global_stats":
            return f"""📊 **Statistiques globales de la base de données :**

- 👨‍🔬 **Chercheurs:** {results.get('total_chercheurs', 0)}
- 📄 **Publications:** {results.get('total_publications', 0)}
- 🏛️ **Institutions:** {results.get('total_institutions', 0)}
- 🤝 **Collaborations:** {results.get('total_collaborations', 0)}
- 🌍 **Pays:** {results.get('nb_pays', 0)}
- 📅 **Période:** {results.get('annee_min', 'N/A')} - {results.get('annee_max', 'N/A')}
"""
        
        elif tool_name == "get_top_publications" and isinstance(results, list):
            lines = ["📄 **Publications les plus citées :**\n"]
            for i, p in enumerate(results, 1):
                auteurs = ', '.join(p.get('auteurs', [])[:2]) if p.get('auteurs') else 'N/A'
                lines.append(f"{i}. **{p.get('titre', 'N/A')[:70]}{'...' if len(p.get('titre', '')) > 70 else ''}**")
                lines.append(f"   _{auteurs}_ ({p.get('annee', 'N/A')}) - **{p.get('citations', 0)} citations**\n")
            return '\n'.join(lines)
        
        elif tool_name == "search_chercheur" and isinstance(results, dict):
            lines = [f"👨‍🔬 **{results.get('nom', 'N/A')}**\n"]
            lines.append(f"📄 **Publications:** {results.get('total_publications', 0)}")
            lines.append(f"🤝 **Collaborateurs:** {results.get('total_collaborateurs', 0)}")
            lines.append(f"🏛️ **Institutions:** {results.get('total_institutions', 0)}\n")
            
            if results.get('publications'):
                lines.append("**📚 Publications récentes :**")
                for p in results['publications'][:5]:
                    lines.append(f"- {p.get('titre', 'N/A')[:60]}... ({p.get('annee', 'N/A')}) - {p.get('citations', 0)} citations")
            
            if results.get('collaborateurs'):
                lines.append(f"\n**🤝 Collaborateurs :** {', '.join(results['collaborateurs'][:10])}...")
            
            return '\n'.join(lines)
        
        elif tool_name == "get_top_institutions" and isinstance(results, list):
            lines = ["🏛️ **Top institutions :**\n"]
            for i, inst in enumerate(results, 1):
                lines.append(f"{i}. **{inst.get('nom', 'N/A')[:50]}**")
                lines.append(f"   📍 {inst.get('pays', 'N/A')} | 👨‍🔬 {inst.get('nb_chercheurs', 0)} chercheurs\n")
            return '\n'.join(lines)
        
        elif tool_name == "search_institution" and isinstance(results, dict):
            lines = [f"🏛️ **{results.get('nom', 'N/A')}**\n"]
            lines.append(f"📍 **Pays:** {results.get('pays', 'N/A')}")
            lines.append(f"📋 **Type:** {results.get('type', 'N/A')}")
            lines.append(f"👨‍🔬 **Chercheurs:** {results.get('total_chercheurs', 0)}")
            lines.append(f"📄 **Publications:** {results.get('total_publications', 0)}")
            return '\n'.join(lines)
        
        elif tool_name == "get_top_collaborations" and isinstance(results, list):
            lines = ["🤝 **Collaborations les plus fortes :**\n"]
            for i, c in enumerate(results, 1):
                lines.append(f"{i}. **{c.get('chercheur1', 'N/A')}** ↔️ **{c.get('chercheur2', 'N/A')}** (poids: {c.get('poids', 0)})")
            return '\n'.join(lines)
        
        
        elif tool_name == "get_stats_pays" and isinstance(results, list):
            lines = ["🌍 **Statistiques par pays :**\n"]
            for r in results[:15]:
                if 'total_publications' in r:
                    lines.append(f"- **{r.get('pays', 'N/A')}**: {r.get('total_publications', 0)} publications")
                else:
                    lines.append(f"- {r.get('pays', 'N/A')} ({r.get('annee', 'N/A')}): {r.get('nombre_publications', 0)} publications")
            return '\n'.join(lines)
        
        elif tool_name == "get_publications_by_year" and isinstance(results, list):
            lines = [f"📅 **Publications ({len(results)} trouvées) :**\n"]
            for p in results[:10]:
                lines.append(f"- **{p.get('titre', 'N/A')[:60]}...** ({p.get('citations', 0)} citations)")
            return '\n'.join(lines)
        
        elif tool_name == "search_publication" and isinstance(results, list):
            lines = [f"📄 **{len(results)} publication(s) trouvée(s) :**\n"]
            for p in results[:5]:
                auteurs = ', '.join(p.get('auteurs', [])[:3]) if p.get('auteurs') else 'N/A'
                lines.append(f"**{p.get('titre', 'N/A')[:70]}**")
                lines.append(f"_{auteurs}_ ({p.get('annee', 'N/A')}) - {p.get('citations', 0)} citations\n")
            return '\n'.join(lines)
        
        elif tool_name == "list_chercheurs" and isinstance(results, list):
            return f"👨‍🔬 **Liste des chercheurs ({len(results)}) :**\n\n" + ', '.join(results)
        
        # Fallback: afficher le JSON formaté
        return f"**Résultats :**\n```json\n{json.dumps(results, ensure_ascii=False, indent=2)[:2000]}\n```"
    
    def _detect_tool_from_question(self, question: str) -> Optional[Dict]:
        """Détecter automatiquement l'outil à utiliser basé sur la question"""
        q = question.lower().strip()
        
        # Salutations - pas d'outil
        if any(word in q for word in ["bonjour", "salut", "hello", "merci", "aide", "help"]):
            return None
        
        # Top publications
        if ("top" in q or "plus cité" in q or "meilleures" in q) and ("publication" in q or "article" in q or "papier" in q or "citées" in q or "cités" in q):
            limit = 10
            for word in q.split():
                if word.isdigit():
                    limit = int(word)
                    break
            return {"tool": "get_top_publications", "params": {"limit": limit}}
        
        # Top chercheurs
        if ("top" in q or "meilleurs" in q) and ("chercheur" in q or "auteur" in q):
            limit = 10
            for word in q.split():
                if word.isdigit():
                    limit = int(word)
                    break
            return {"tool": "get_top_chercheurs", "params": {"limit": limit}}
        
        # Top institutions
        if ("top" in q or "meilleures" in q) and ("institution" in q or "université" in q):
            limit = 10
            for word in q.split():
                if word.isdigit():
                    limit = int(word)
                    break
            return {"tool": "get_top_institutions", "params": {"limit": limit}}
        
        # Top collaborations
        if ("top" in q or "meilleures" in q or "plus fortes" in q) and "collaboration" in q:
            limit = 10
            for word in q.split():
                if word.isdigit():
                    limit = int(word)
                    break
            return {"tool": "get_top_collaborations", "params": {"limit": limit}}
        
        # Stats globales
        if ("statistique" in q or "stats" in q or "combien" in q) and ("global" in q or "total" in q or "base" in q or "tout" in q):
            return {"tool": "get_global_stats", "params": {}}
        
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
        
        # Publications par année
        import re
        year_match = re.search(r'\b(19\d{2}|20\d{2})\b', q)
        if year_match and ("publication" in q or "article" in q or "année" in q or "en " in q):
            return {"tool": "get_publications_by_year", "params": {"annee": int(year_match.group(1))}}
        
        # Recherche chercheur
        if "qui est" in q or "chercheur" in q or "auteur" in q or "info sur" in q:
            # Extraire le nom (mots avec majuscules)
            words = question.split()
            name_parts = [w for w in words if w and w[0].isupper() and len(w) > 1 and w.lower() not in ["qui", "est", "le", "la", "les", "de", "du"]]
            if name_parts:
                return {"tool": "search_chercheur", "params": {"nom": " ".join(name_parts)}}
        
        # Recherche institution
        if "institution" in q or "université" in q or "labo" in q:
            words = question.split()
            name_parts = [w for w in words if w and w[0].isupper() and len(w) > 1]
            if name_parts:
                return {"tool": "search_institution", "params": {"nom": " ".join(name_parts)}}
        
        # Collaborations d'un chercheur
        if "collaboration" in q:
            words = question.split()
            name_parts = [w for w in words if w and w[0].isupper() and len(w) > 1]
            if name_parts:
                return {"tool": "get_collaborations", "params": {"chercheur": " ".join(name_parts)}}
        
        # Recherche publication
        if "publication" in q or "article" in q or "papier" in q:
            words = question.split()
            # Prendre les mots significatifs
            keywords = [w for w in words if len(w) > 3 and w.lower() not in ["publication", "article", "papier", "recherche", "trouve", "cherche", "sur", "avec", "dans"]]
            if keywords:
                return {"tool": "search_publication", "params": {"titre": " ".join(keywords[:3])}}
        
        # Liste chercheurs
        if "liste" in q and "chercheur" in q:
            return {"tool": "list_chercheurs", "params": {}}
        
        # Recherche générique par nom propre
        words = question.split()
        name_parts = [w for w in words if w and w[0].isupper() and len(w) > 2 and w.lower() not in ["qui", "est", "que", "quoi", "comment", "pourquoi"]]
        if name_parts:
            return {"tool": "search_chercheur", "params": {"nom": " ".join(name_parts)}}
        
        # Défaut: stats globales si aucune correspondance
        return {"tool": "get_global_stats", "params": {}}
    
    def chat(self, user_message: str) -> str:
        """Traiter un message utilisateur et retourner une réponse"""
        
        # Vérifier si c'est une salutation simple
        q_lower = user_message.lower().strip()
        if any(word in q_lower for word in ["bonjour", "salut", "hello", "hi", "coucou"]):
            stats = self.mcp.get_global_stats()
            return f"""👋 **Bonjour !** Je suis votre assistant pour explorer la base de données de recherche.

📊 **La base contient :**
- 👨‍🔬 {stats['total_chercheurs']} chercheurs
- 📄 {stats['total_publications']} publications  
- 🏛️ {stats['total_institutions']} institutions

**Posez-moi vos questions !**"""
        
        if any(word in q_lower for word in ["aide", "help", "comment"]):
            return """🆘 **Voici ce que je peux faire :**

**🔍 Recherches :**
- "Qui est Salamatian ?" - Infos sur un chercheur
- "Publication traffic" - Chercher une publication
- "Université de Lille" - Infos sur une institution 

**🏆 Classements :**
- "Top 10 publications" - Articles les plus cités
- "Top chercheurs" - Chercheurs les plus productifs
- "Top institutions" - Institutions avec lequel les chercheurs collaborent le plus
- "Top collaborations" - Paires de chercheurs qui collaborent le plus

**📊 Statistiques :**
- "Stats globales" - Vue d'ensemble
- "Stats France" - Publications par pays
- "Publications 2020" - Articles d'une année"""
        
        # Étape 1: D'abord essayer de détecter l'outil automatiquement
        tool_call = self._detect_tool_from_question(user_message)
        
        # Étape 2: Si pas de détection automatique, demander au LLM
        if tool_call is None:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            llm_response = self._call_llm(messages, temperature=0.1)
            tool_call = self._parse_tool_call(llm_response)
        
        # Étape 3: Exécuter l'outil si trouvé
        if tool_call:
            tool_name = tool_call.get("tool", "")
            params = tool_call.get("params", {})
            
            # Exécuter l'outil MCP
            tool_result = self.mcp.execute_tool(tool_name, **params)
            
            # Formater les résultats
            final_response = self._format_results_as_text(tool_name, tool_result, user_message)
            
            # Optionnel: Demander au LLM d'améliorer la présentation
            if len(str(tool_result)) < 2000:
                try:
                    result_str = json.dumps(tool_result, ensure_ascii=False, indent=2)
                    followup_messages = [
                        {"role": "system", "content": "Présente ces résultats de manière claire et concise avec des emojis. Ne montre PAS le JSON brut. Sois direct et informatif."},
                        {"role": "user", "content": f"Question: {user_message}\n\nDonnées:\n{result_str}"}
                    ]
                    llm_formatted = self._call_llm(followup_messages, temperature=0.3)
                    
                    # Utiliser la réponse du LLM seulement si elle semble valide
                    if len(llm_formatted) > 50 and not llm_formatted.strip().startswith('{'):
                        final_response = llm_formatted
                except:
                    pass  # Garder le formatage par défaut
        else:
            final_response = "Je n'ai pas compris votre question. Essayez par exemple:\n- 'Top 10 publications'\n- 'Qui est Salamatian ?'\n- 'Stats globales'"
        
        # Sauvegarder dans l'historique
        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": final_response})
        
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
        
        return final_response
    
    def clear_history(self):
        """Effacer l'historique de conversation"""
        self.conversation_history = []