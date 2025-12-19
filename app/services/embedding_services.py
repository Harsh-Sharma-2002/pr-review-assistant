import os
import requests
import json
from sentence_transformers import SentenceTransformer
from typing import Optional

# Load local model once
_local_model = SentenceTransformer("all-MiniLM-L6-v2")


########################################################################################################
# Helper: wrap output
def _wrap(embedding: list[float], provider: str):
    return {
        "embedding": embedding,
        "provider": provider
    }

########################################################################################################
# LOCAL FALLBACK
def embed_local(text: str):
    """Local fallback embedding using MiniLM."""
    emb = _local_model.encode(text).tolist()
    return _wrap(emb, "local")


########################################################################################################
# OPENAI
def embed_openai(text: str, api_key: str):
    url = "https://api.openai.com/v1/embeddings"
    payload = {"model": "text-embedding-3-large", "input": text}
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    try:
        resp = requests.post(url, headers=headers, data=json.dumps(payload))
        resp.raise_for_status()
        emb = resp.json()["data"][0]["embedding"]
        return _wrap(emb, "openai")
    except Exception as e:
        raise Exception(f"OpenAI embedding error → {resp.text if 'resp' in locals() else str(e)}")


########################################################################################################
# GEMINI
def embed_gemini(text: str, api_key: str):
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        "text-embedding-004:embedText?key="
        + api_key
    )
    payload = {"text": text}

    try:
        resp = requests.post(url, json=payload)
        resp.raise_for_status()
        emb = resp.json()["embedding"]["values"]
        return _wrap(emb, "gemini")
    except Exception as e:
        raise Exception(f"Gemini embedding error → {resp.text if 'resp' in locals() else str(e)}")


########################################################################################################
# CLAUDE (NO REAL EMBEDDINGS)
def embed_claude(text: str, api_key: str):
    """
    Anthropic has no embedding endpoint.
    We use local embedding but label provider as 'claude-fallback'
    """
    try:
        emb = _local_model.encode(text).tolist()
        return _wrap(emb, "claude-fallback")
    except Exception as e:
        raise Exception(f"Claude fallback embedding error → {str(e)}")


########################################################################################################
# MAIN EMBEDDING LOGIC
def embed_text(text: str, provider: Optional[str] = None):
    """
    Returns:
    {
        "embedding": [...],
        "provider": "openai" | "gemini" | "claude-fallback" | "local"
    }

    Provider selection:
        EXPLICIT MODE:
            - If provider requested, use that or return clear error
        AUTO MODE:
            - Try OpenAI → Gemini → Claude → Local
    """

    openai_key = os.getenv("OPENAI_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    claude_key = os.getenv("ANTHROPIC_API_KEY")

 
    # EXPLICIT PROVIDER MODE
    
    if provider:
        provider = provider.lower()

        try:
            if provider == "openai":
                if not openai_key:
                    return {"error": "Missing OPENAI_API_KEY"}
                return embed_openai(text, openai_key)

            if provider == "gemini":
                if not gemini_key:
                    return {"error": "Missing GEMINI_API_KEY"}
                return embed_gemini(text, gemini_key)

            if provider == "claude":
                if not claude_key:
                    return {"error": "Missing ANTHROPIC_API_KEY"}
                return embed_claude(text, claude_key)

            if provider == "local":
                return embed_local(text)

            return {"error": f"Unknown provider '{provider}'."}

        except Exception as e:
            return {
                "error": f"Provider '{provider}' failed.",
                "details": str(e)
            }

   
    # AUTO-SELECTION MODE WITH ERROR LOGGING
  
    errors = []

    if openai_key:
        try:
            return embed_openai(text, openai_key)
        except Exception as e:
            errors.append({"provider": "openai", "error": str(e)})

    if gemini_key:
        try:
            return embed_gemini(text, gemini_key)
        except Exception as e:
            errors.append({"provider": "gemini", "error": str(e)})

    if claude_key:
        try:
            return embed_claude(text, claude_key)
        except Exception as e:
            errors.append({"provider": "claude-fallback", "error": str(e)})

    # Local never fails unless machine is broken
    try:
        return embed_local(text)
    except Exception as e:
        errors.append({"provider": "local", "error": str(e)})

    # If absolutely everything failed:
    return {
        "error": "All embedding providers failed.",
        "attempts": errors
    }

