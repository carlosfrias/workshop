#!/usr/bin/env python3
"""
rag-retrieve.py — RAG Retrieval API for Carlos' Desktop Memory
Uses Ollama (fnet3) for query embeddings + ChromaDB (fnet3) for semantic search.

Usage:
  python3 rag-retrieve.py "query text"
  python3 rag-retrieve.py "query"
  python3 rag-retrieve.py "query" --use-orchestrator   # Use Mac M4 Pro for query embedding --top-k 5
  python3 rag-retrieve.py "query"
  python3 rag-retrieve.py "query" --use-orchestrator   # Use Mac M4 Pro for query embedding --domain wiki
  python3 rag-retrieve.py --test
"""
import os, sys, json, argparse, requests
from typing import List, Dict, Optional

CHROMA_HOST = os.getenv("CHROMA_HOST", "192.168.0.143")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "192.168.0.143")
OLLAMA_PORT = int(os.getenv("OLLAMA_PORT", "11434"))
CHROMA_URL = f"http://{CHROMA_HOST}:{CHROMA_PORT}"
OLLAMA_URL = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}"
COLLECTION_NAME = "carlos_desktop_memory"
EMBEDDING_MODEL = "nomic-embed-text"
UUID_FILE = os.path.join(os.path.dirname(__file__), ".chromadb-uuid")


def get_embedding(text: str) -> List[float]:
    """Generate embedding via Ollama."""
    payload = {"model": EMBEDDING_MODEL, "prompt": text}
    try:
        r = requests.post(f"{OLLAMA_URL}/api/embeddings", json=payload, timeout=60)
        r.raise_for_status()
        data = r.json()
        emb = data.get("embedding")
        if not emb or not isinstance(emb, list):
            print(f"⚠️  Bad embedding for query: {text[:50]}...")
            return []
        return emb
    except Exception as e:
        print(f"❌ Embedding failed: {e}")
        return []


class ChromaDBHttpClient:
    """HTTP client for ChromaDB with UUID persistence."""

    def __init__(self, host=CHROMA_HOST, port=CHROMA_PORT):
        self.base = f"http://{host}:{port}/api/v1"
        self.uuid = ""
        if os.path.exists(UUID_FILE):
            with open(UUID_FILE) as f:
                self.uuid = f.read().strip()

    def _req(self, method, path, **kwargs):
        url = f"{self.base}{path}"
        try:
            r = requests.request(method, url, timeout=30, **kwargs)
            if r.status_code >= 400:
                print(f"⚠️  HTTP {r.status_code}: {r.text[:200]}", file=sys.stderr)
            return r
        except Exception as e:
            print(f"❌ Request failed: {e}", file=sys.stderr)
            return None

    def heartbeat(self) -> bool:
        return self._req("GET", "/heartbeat") is not None

    def collection_exists(self, name: str) -> bool:
        if not self.uuid:
            return False
        r = self._req("GET", f"/collections/{self.uuid}/count")
        return r is not None and r.status_code == 200

    def query(self, query_embeddings: List[List[float]], n_results: int = 5,
              where: dict = None, include: List[str] = None):
        if not self.uuid:
            return None
        payload = {
            "query_embeddings": query_embeddings,
            "n_results": n_results,
        }
        if where:
            payload["where"] = where
        if include:
            payload["include"] = include
        r = self._req("POST", f"/collections/{self.uuid}/query", json=payload)
        if r and r.status_code == 200:
            return r.json()
        return None


def retrieve(query: str, top_k: int = 5, domain: Optional[str] = None,
             since: Optional[str] = None, doc_type: Optional[str] = None) -> List[Dict]:
    client = ChromaDBHttpClient()

    if not client.collection_exists(COLLECTION_NAME):
        print(f"❌ Collection '{COLLECTION_NAME}' not found. Run indexing first.")
        return []

    # Generate query embedding
    emb = get_embedding(query)
    if not emb:
        return []

    where_filter = {}
    if domain:
        where_filter["domain"] = domain
    if doc_type:
        where_filter["doc_type"] = doc_type

    results = client.query(
        query_embeddings=[emb],
        n_results=top_k * 3,
        where=where_filter if where_filter else None,
        include=["documents", "metadatas", "distances"],
    )

    if not results:
        return []

    ids = results.get("ids", [[]])[0]
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    dists = results.get("distances", [[]])[0]

    output = []
    for i in range(len(ids)):
        meta = metas[i] if i < len(metas) else {}
        if since and meta:
            doc_date = meta.get("doc_date") if isinstance(meta, dict) else ""
            if doc_date and str(doc_date) < since:
                continue
        output.append({
            "id": ids[i], "text": docs[i] if i < len(docs) else "",
            "distance": dists[i] if i < len(dists) else 0.0,
            "metadata": meta if isinstance(meta, dict) else {},
        })
    output.sort(key=lambda x: x["distance"])
    return output[:top_k]


def format_results(results: List[Dict], format_type: str, query: str = "") -> str:
    if format_type == "json":
        return json.dumps(results, indent=2, default=str)

    lines = [f"# RAG Retrieval Results\n", f"Query: *{query}*\n", f"Results: {len(results)}\n", "---\n"]
    for i, doc in enumerate(results, 1):
        meta = doc.get("metadata", {})
        lines.append(f"## {i}. 📄 {meta.get('filename', 'Unknown')}")
        lines.append(f"- **Domain:** `{meta.get('domain', 'unknown')}`")
        lines.append(f"- **Type:** {meta.get('doc_type', 'unknown')}")
        lines.append(f"- **Date:** {meta.get('doc_date', 'unknown')}")
        lines.append(f"- **Relevance:** {1.0 - doc['distance']:.3f}")
        text = doc.get('text', '')[:500]
        lines.append(f"\n**Content:**\n```\n{text}...\n```\n")
    return "\n".join(lines)


def test_connection():
    client = ChromaDBHttpClient()
    chroma_ok = client.heartbeat()
    emb = get_embedding("test")
    emb_ok = len(emb) > 0
    if chroma_ok and emb_ok:
        print(f"✅ ChromaDB RAG Connection OK")
        print(f"   ChromaDB: {CHROMA_URL}")
        print(f"   Ollama: {OLLAMA_URL} (model: {EMBEDDING_MODEL})")
        print(f"   Collection: {COLLECTION_NAME}")
        print(f"   Embedding dim: {len(emb)}")
        return True
    print(f"❌ RAG test failed: ChromaDB={chroma_ok}, Embeddings={emb_ok}")
    return False


def main():
    parser = argparse.ArgumentParser(description="Carlos' Desktop RAG Retrieval")
    parser.add_argument("query", nargs="?", help="Search query")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--domain", type=str)
    parser.add_argument("--since", type=str)
    parser.add_argument("--doc-type", type=str)
    parser.add_argument("--format", type=str, choices=["json", "markdown"], default="markdown")
    parser.add_argument("--test", action="store_true")
    parser.add_argument("--use-orchestrator", action="store_true", help="Use orchestrator (127.0.0.1) for query embedding")
    args = parser.parse_args()

    global OLLAMA_URL
    if args.use_orchestrator:
        OLLAMA_URL = "http://127.0.0.1:11434"
        print("Using orchestrator (127.0.0.1:11434) for query embedding")

    if args.test:
        return test_connection()

    if not args.query:
        parser.print_help()
        return False

    results = retrieve(
        query=args.query,
        top_k=args.top_k,
        domain=args.domain,
        since=args.since,
        doc_type=args.doc_type,
    )

    print(format_results(results, args.format, args.query))
    return True


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
