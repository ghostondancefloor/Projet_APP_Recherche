"""
thesis_gen_grok.py
------------------
- Reads local publications.bson
- Filters docs where 'auteurs' contains the author
- Extracts titles
- Uses OpenAlex to infer author domain + topics
- Pulls trending topics ONLY in that domain
- Fetches evidence papers for 3 target topics
- Calls Grok (xAI) to generate 3 concrete thesis ideas + mini-abstracts grounded in evidence

Docs:
- xAI base: https://api.x.ai
- Chat Completions: POST https://api.x.ai/v1/chat/completions
- Auth: Authorization: Bearer <xAI API key>
"""

import argparse
import json
import os
import time
import difflib
import re
from datetime import date, timedelta
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple

import requests
import bson  # From pymongo package





OPENALEX_BASE = "https://api.openalex.org"
GROQ_CHAT_COMPLETIONS = "https://api.groq.com/openai/v1/chat/completions"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # Load from .env file





# ----------------------------
# BSON helpers
# ----------------------------

STOPWORDS = {
    "the","a","an","and","or","of","for","to","in","on","with","by","from","via","using",
    "study","analysis","approach","method","methods","model","models","based","data",
    "towards","toward","new","novel","framework","system","application","applications"
}

def top_keywords_from_titles(titles: List[str], k: int = 10) -> List[str]:
    tokens = []
    for t in titles:
        t = (t or "").lower()
        words = re.findall(r"[a-zA-Z]{3,}", t)  # keep letters only
        tokens.extend([w for w in words if w not in STOPWORDS])
    counts = Counter(tokens)
    return [w for w, _ in counts.most_common(k)]


def load_bson_docs(path: str) -> List[Dict[str, Any]]:
    with open(path, "rb") as f:
        return list(bson.decode_file_iter(f))


def _norm(s: str) -> str:
    return (s or "").strip().lower()


def auteurs_contains(doc: Dict[str, Any], needle: str) -> bool:
    needle_n = _norm(needle)
    if not needle_n:
        return False
    a = doc.get("auteurs")
    if a is None:
        return False

    if isinstance(a, str):
        return needle_n in _norm(a)

    if isinstance(a, list):
        for item in a:
            if isinstance(item, str) and needle_n in _norm(item):
                return True
            if isinstance(item, dict):
                for k in ("name", "full_name", "author", "auteur", "nom"):
                    v = item.get(k)
                    if isinstance(v, str) and needle_n in _norm(v):
                        return True
        return False

    return False

def extract_json_from_text(text: str) -> Dict[str, Any]:
    """
    Extract a JSON object from an LLM response that may include extra text or code fences.
    """
    if not text or not text.strip():
        raise ValueError("Model returned empty content.")

    s = text.strip()

    # Try direct JSON
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        pass

    # Try ```json ... ```
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", s, flags=re.DOTALL)
    if m:
        return json.loads(m.group(1))

    # Try first {...} block
    m = re.search(r"(\{.*\})", s, flags=re.DOTALL)
    if m:
        return json.loads(m.group(1))

    raise ValueError(f"Could not parse JSON. Output starts with: {s[:300]}")



def extract_title(doc: Dict[str, Any]) -> Optional[str]:
    for k in ("title", "titre", "article_title", "paper_title", "publication_title", "work_title"):
        v = doc.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


# ----------------------------
# OpenAlex helpers
# ----------------------------
def openalex_get(path: str, params: Dict[str, Any], timeout: int = 30) -> Dict[str, Any]:
    headers = {"User-Agent": "thesis-gen-grok/0.1"}
    api_key = os.getenv("OPENALEX_API_KEY")  # optional
    if api_key:
        params = dict(params)
        params["api_key"] = api_key
    r = requests.get(f"{OPENALEX_BASE}{path}", params=params, headers=headers, timeout=timeout)
    r.raise_for_status()
    return r.json()


def best_work_for_title(
    title: str,
    per_page: int = 5,
    min_ratio: float = 0.58,
    sleep_s: float = 0.12
) -> Optional[Dict[str, Any]]:
    q = (title or "").strip()
    if not q:
        return None

    data = openalex_get("/works", {
        "search": q,
        "per-page": per_page,
        "select": "id,title,display_name,primary_topic,publication_date,cited_by_count",
    })
    time.sleep(sleep_s)

    results = data.get("results", [])
    if not results:
        return None

    qn = _norm(q)
    best, best_ratio = None, 0.0
    for w in results:
        wt = w.get("title") or w.get("display_name") or ""
        ratio = difflib.SequenceMatcher(None, qn, _norm(wt)).ratio()
        if ratio > best_ratio:
            best_ratio, best = ratio, w

    if not best or best_ratio < min_ratio:
        return None

    best["_match_ratio"] = best_ratio
    return best


def build_author_profile(titles: List[str], max_titles: int = 60) -> Dict[str, Any]:
    matched = []
    topic_counts = Counter()
    domain_counts = Counter()

    for t in titles[:max_titles]:
        w = best_work_for_title(t)
        if not w:
            continue
        matched.append(w)

        pt = w.get("primary_topic")
        if isinstance(pt, dict):
            if pt.get("display_name"):
                topic_counts[pt["display_name"]] += 1
            dom = pt.get("domain")
            if isinstance(dom, dict) and dom.get("id"):
                domain_counts[dom["id"]] += 1

    dom_id = domain_counts.most_common(1)[0][0] if domain_counts else None
    dom_name = None
    if dom_id:
        for w in matched:
            pt = w.get("primary_topic") or {}
            dom = pt.get("domain") or {}
            if dom.get("id") == dom_id:
                dom_name = dom.get("display_name")
                break

    return {
        "matched_works": matched,
        "author_topics": topic_counts,
        "domain_id": dom_id,
        "domain_name": dom_name or dom_id or "ALL",
    }


def trending_topics_in_domain(domain_id: Optional[str], days: int = 180, max_works: int = 1200, sleep_s: float = 0.12) -> Counter:
    today = date.today()
    start = today - timedelta(days=days)

    scope = f",primary_topic.domain.id:{domain_id}" if domain_id else ""

    params = {
        "filter": f"from_publication_date:{start.isoformat()},to_publication_date:{today.isoformat()}{scope}",
        "per-page": 200,
        "cursor": "*",
        "select": "id,primary_topic,cited_by_count,publication_date,title,display_name",
        "sort": "cited_by_count:desc",
    }

    counts = Counter()
    fetched = 0
    while True:
        data = openalex_get("/works", params=params)
        time.sleep(sleep_s)

        results = data.get("results", [])
        if not results:
            break

        for w in results:
            pt = w.get("primary_topic")
            if isinstance(pt, dict) and pt.get("display_name"):
                counts[pt["display_name"]] += 1
            fetched += 1
            if fetched >= max_works:
                return counts

        nxt = data.get("meta", {}).get("next_cursor")
        if not nxt:
            break
        params["cursor"] = nxt

    return counts

def evidence_works_for_topic(topic_name: str, extra_terms: List[str], days: int = 365, k: int = 8, sleep_s: float = 0.12) -> List[Dict[str, Any]]:
    today = date.today()
    start = today - timedelta(days=days)

    # Build a more specific query: topic + a few niche terms
    extra_terms = [t for t in extra_terms if t and len(t) >= 3][:5]
    query = topic_name if not extra_terms else f"{topic_name} " + " ".join(extra_terms)

    data = openalex_get("/works", {
        "search": query,
        "filter": f"from_publication_date:{start.isoformat()},to_publication_date:{today.isoformat()}",
        "per-page": 50,
        "select": "id,title,display_name,publication_date,cited_by_count,primary_topic,abstract_inverted_index",
        "sort": "cited_by_count:desc",
    })
    time.sleep(sleep_s)

    res = data.get("results", [])[:k]
    out = []
    for w in res:
        out.append({
            "id": w.get("id"),
            "title": w.get("title") or w.get("display_name"),
            "publication_date": w.get("publication_date"),
            "cited_by_count": w.get("cited_by_count"),
            "primary_topic": (w.get("primary_topic") or {}).get("display_name") if isinstance(w.get("primary_topic"), dict) else None
        })
    return out



# ----------------------------
# xAI (Grok) generation
# ----------------------------
def groq_chat_json(model: str, prompt_payload: dict, temperature: float = 0.2, timeout: int = 120) -> dict:
    api_key = GROQ_API_KEY

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    schema = {
        "title": "string",
        "research_question": "string",
        "mini_abstract": "string (6-9 sentences, concrete)",
        "method_plan": ["5-8 short bullet steps"],
        "datasets_or_data": ["list strings"],
        "evaluation": ["list strings"],
        "evidence_ids": ["list of evidence_papers[].id used (no inventions)"],
    }

    system_msg = (
        "You are a research advisor.\n"
        "Return ONLY a valid JSON object. No markdown. No code fences. No extra text.\n"
        "Ground everything ONLY in the provided evidence papers.\n"
        "Rules:\n"
        "- Do NOT invent citations.\n"
        "- evidence_ids must be chosen ONLY from evidence_papers[].id.\n"
        "- Be specific about method and evaluation.\n"
        "Title must include at least 2 specific technical terms (e.g., dataset/task + method).\n"
        "Do not use generic titles like 'A Study of...' or 'An Analysis of...'.\n"

    )

    user_msg = {"input": prompt_payload, "output_schema": schema}

    body = {
        "model": model,
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": json.dumps(user_msg, ensure_ascii=False)}
        ],
    }

    # Retry with exponential backoff for rate limits and JSON parsing
    max_retries = 5
    base_delay = 2
    
    for attempt in range(max_retries):
        try:
            r = requests.post(GROQ_CHAT_COMPLETIONS, headers=headers, json=body, timeout=timeout)

            # Handle rate limiting with exponential backoff
            if r.status_code == 429:
                if attempt < max_retries - 1:
                    wait_time = base_delay * (2 ** attempt)
                    print(f"Rate limit hit. Waiting {wait_time}s before retry {attempt + 1}/{max_retries}...")
                    time.sleep(wait_time)
                    continue
                else:
                    print("Max retries reached for rate limit.")
                    r.raise_for_status()
            
            # Handle other HTTP errors
            if not r.ok:
                print("Groq status:", r.status_code)
                print("Groq response:", r.text)
                r.raise_for_status()

            content = r.json()["choices"][0]["message"]["content"]

            try:
                return extract_json_from_text(content)
            except Exception as e:
                if attempt < 1:  # Only retry JSON parsing once
                    # Make it even stricter on retry
                    body["temperature"] = 0
                    body["messages"][0]["content"] = (
                        system_msg
                        + "\nIMPORTANT: Output must start with '{' and end with '}'. Return JSON only."
                    )
                    time.sleep(1)  # Brief delay before JSON retry
                    continue

                print("\n--- RAW MODEL OUTPUT (FAILED JSON PARSE) ---")
                print((content or "")[:2000])
                print("--- END ---\n")
                raise e
        
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = base_delay * (2 ** attempt)
                print(f"Request failed: {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue
            raise




def generate_three_with_grok(
    model: str,
    author: str,
    domain_name: str,
    author_titles: List[str],
    author_topics: List[Tuple[str, int]],
    targets: List[str],
) -> List[Dict[str, Any]]:
    ideas = []
    for i, ttopic in enumerate(targets):
        kw = top_keywords_from_titles(author_titles, k=12)
        evidence = evidence_works_for_topic(ttopic, extra_terms=kw, days=365, k=8)
        payload = {
            "author_name": author,
            "inferred_domain": domain_name,
            "author_top_topics": author_topics[:10],
            "target_trending_topic": ttopic,
            "evidence_papers": evidence,
            "constraints": {
                "must_be_concrete": True,
                "must_include_plan": True,
                "must_include_evaluation": True
            }
        }
        
        # Add delay between API calls to avoid rate limiting
        if i > 0:
            time.sleep(3)  # Wait 3 seconds between consecutive calls
        
        idea = groq_chat_json(model=model, prompt_payload=payload, temperature=0.3)
        ideas.append(idea)
    return ideas


# ----------------------------
# Main
# ----------------------------
def main():
    ap = argparse.ArgumentParser(description="OpenAlex + Grok (xAI) thesis generator (3 ideas with mini-abstracts)")
    ap.add_argument("--bson", required=True, help="Path to publications.bson")
    ap.add_argument("--author", required=True, help="Author name to match in 'auteurs' (e.g., 'joe doe')")
    ap.add_argument("--model", default="llama-3.3-70b-versatile", help="Groq model id (e.g., llama-3.3-70b-versatile)")
    ap.add_argument("--max-author-titles", type=int, default=60)
    ap.add_argument("--trend-days", type=int, default=180)
    ap.add_argument("--trend-max-works", type=int, default=1200)
    ap.add_argument("--export", default="thesis_out.json")
    ap.add_argument("--debug", action="store_true")
    args = ap.parse_args()

    # 1) Load BSON and extract titles
    docs = load_bson_docs(args.bson)
    matched_docs = [d for d in docs if auteurs_contains(d, args.author)]
    titles = [extract_title(d) for d in matched_docs]
    titles = [t for t in titles if t]

    print(f"Matched docs: {len(matched_docs)} | titles: {len(titles)}")
    if not titles:
        print("❌ No titles found. Check 'auteurs' or title keys.")
        if matched_docs:
            print(json.dumps(matched_docs[0], ensure_ascii=False, indent=2)[:1500])
        return

    # 2) Build author profile via OpenAlex
    profile = build_author_profile(titles, max_titles=args.max_author_titles)
    author_topics = profile["author_topics"]
    domain_id = profile["domain_id"]
    domain_name = profile["domain_name"]

    if not author_topics:
        print("❌ Could not infer topics from titles via OpenAlex matching.")
        print("Try lowering min_ratio in best_work_for_title(), or increase --max-author-titles.")
        return

    print(f"Inferred domain: {domain_name}")
    print("Top author topics:", author_topics.most_common(5))

    # 3) Trending topics within inferred domain
    trends = trending_topics_in_domain(domain_id, days=args.trend_days, max_works=args.trend_max_works)
    top_trending = [t for t, _ in trends.most_common(30)]

    # 4) Choose 3 target topics (prefer overlap)
    top_author = [t for t, _ in author_topics.most_common(10)]
    overlap = [t for t in top_author if t in set(top_trending)]
    targets = overlap[:3] if overlap else top_trending[:3]

    # Ensure exactly 3
    if len(targets) < 3:
        for t in top_author:
            if t not in targets:
                targets.append(t)
            if len(targets) == 3:
                break

    print("Chosen topics:", targets)

    # 5) Generate with Grok
    print(f"\nGenerating 3 thesis ideas using xAI model '{args.model}' ...")
    ideas = generate_three_with_grok(
    model=args.model,
    author=args.author,
    domain_name=domain_name,
    author_topics=author_topics.most_common(15),
    targets=targets,
    author_titles=titles
)


    # 6) Save
    payload = {
        "author": args.author,
        "inferred_domain": domain_name,
        "top_author_topics": author_topics.most_common(20),
        "chosen_trending_topics": targets,
        "ideas": ideas,
    }

    with open(args.export, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print("\n✅ Saved to:", args.export)
    print("\n=== Preview ===")
    for i, idea in enumerate(ideas, 1):
        print(f"\n{i}) {idea.get('title')}")
        print("RQ:", idea.get("research_question"))
        print("Evidence IDs:", idea.get("evidence_ids", []))

    if args.debug:
        print("\nTip: If JSON parsing fails, set temperature to 0.2 or reduce evidence papers to 6-8.")

def generate_thesis_ideas_from_researcher_data(
    researcher_data: Dict[str, Any],
    model: str = "llama-3.3-70b-versatile",
    max_titles: int = 60,
    trend_days: int = 180,
    trend_max_works: int = 1200
) -> Dict[str, Any]:
    """
    Generate 3 thesis ideas from researcher data obtained from researchMCPServer.
    
    Args:
        researcher_data: JSON data from researchMCPServer.search_chercheur()
        model: Groq model to use
        max_titles: Maximum number of titles to analyze
        trend_days: Days to look back for trending topics
        trend_max_works: Maximum works to fetch for trending analysis
        
    Returns:
        Dict containing author info, domain, topics, and 3 thesis ideas
    """
    
    # Check for error in researcher data
    if "error" in researcher_data:
        raise ValueError(f"Researcher not found: {researcher_data['error']}")
    
    # Extract publication titles from researcher data
    publications = researcher_data.get("publications", [])
    if not publications:
        raise ValueError("No publications found for this researcher")
    
    # Extract titles from publications
    titles = []
    for pub in publications:
        title = extract_title(pub)
        if title:
            titles.append(title)
    
    if not titles:
        raise ValueError("Could not extract any valid titles from publications")
    
    print(f"Found {len(titles)} publication titles")
    
    # Build author profile via OpenAlex
    print("Building author profile from OpenAlex...")
    profile = build_author_profile(titles, max_titles=max_titles)
    author_topics = profile["author_topics"]
    domain_id = profile["domain_id"]
    domain_name = profile["domain_name"]
    
    if not author_topics:
        raise ValueError("Could not infer topics from titles via OpenAlex matching")
    
    print(f"Inferred domain: {domain_name}")
    print(f"Top author topics: {author_topics.most_common(5)}")
    
    # Get trending topics within inferred domain
    print("Fetching trending topics in domain...")
    trends = trending_topics_in_domain(domain_id, days=trend_days, max_works=trend_max_works)
    top_trending = [t for t, _ in trends.most_common(30)]
    
    # Choose 3 target topics (prefer overlap between author topics and trending)
    top_author = [t for t, _ in author_topics.most_common(10)]
    overlap = [t for t in top_author if t in set(top_trending)]
    targets = overlap[:3] if overlap else top_trending[:3]
    
    # Ensure exactly 3 targets
    if len(targets) < 3:
        for t in top_author:
            if t not in targets:
                targets.append(t)
            if len(targets) == 3:
                break
    
    # Fill remaining with trending if still < 3
    if len(targets) < 3:
        for t in top_trending:
            if t not in targets:
                targets.append(t)
            if len(targets) == 3:
                break
    
    print(f"Chosen target topics: {targets}")
    
    # Generate 3 thesis ideas with Groq
    print(f"Generating 3 thesis ideas using model '{model}'...")
    ideas = generate_three_with_grok(
        model=model,
        author=researcher_data.get("nom", "Researcher"),
        domain_name=domain_name,
        author_topics=author_topics.most_common(15),
        targets=targets,
        author_titles=titles
    )
    
    # Prepare result
    result = {
        "author": researcher_data.get("nom"),
        "inferred_domain": domain_name,
        "top_author_topics": [{"topic": t, "count": c} for t, c in author_topics.most_common(20)],
        "chosen_trending_topics": targets,
        "total_publications": researcher_data.get("total_publications", len(publications)),
        "ideas": ideas,
    }
    
    print("✅ Successfully generated 3 thesis ideas!")
    return result

if __name__ == "__main__":
    main()


