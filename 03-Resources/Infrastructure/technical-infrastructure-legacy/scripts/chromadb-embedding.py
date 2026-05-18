#!/usr/bin/env python3
"""
chromadb-embedding.py — Embedding Pipeline for Carlos' Desktop Session Memory
Uses Ollama (fnet3 or orchestrator) for embeddings + ChromaDB (fnet3) for storage.

Usage:
  python3 chromadb-embedding.py --index-all
  python3 chromadb-embedding.py --index-all --use-orchestrator   # Use Mac M4 Pro for embeddings
  python3 chromadb-embedding.py --incremental
  python3 chromadb-embedding.py --file path/to/doc.md
  python3 chromadb-embedding.py --test
  python3 chromadb-embedding.py --stats
"""
import os, sys, hashlib, json, argparse, glob, requests
from datetime import datetime
from typing import List, Dict

CHROMA_HOST = os.getenv("CHROMA_HOST", "192.168.0.143")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "192.168.0.143")
OLLAMA_PORT = int(os.getenv("OLLAMA_PORT", "11434"))
COLLECTION_NAME = "carlos_desktop_memory"
EMBEDDING_MODEL = "nomic-embed-text"
CHROMA_URL = f"http://{CHROMA_HOST}:{CHROMA_PORT}"
OLLAMA_URL = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}"

WIKI_ROOT = os.path.join(os.path.dirname(__file__), "..", "wiki", "operational")
SUPPORTED_DIRS = ["sessions", "status"]
UUID_FILE = os.path.join(os.path.dirname(__file__), ".chromadb-uuid")


def get_embedding(text: str) -> List[float]:
    """Generate embedding via Ollama on fnet3."""
    payload = {"model": EMBEDDING_MODEL, "prompt": text}
    try:
        r = requests.post(f"{OLLAMA_URL}/api/embeddings", json=payload, timeout=60)
        r.raise_for_status()
        data = r.json()
        emb = data.get("embedding")
        if not emb or not isinstance(emb, list):
            print(f"⚠️  Bad embedding for text: {text[:50]}...")
            return []
        return emb
    except Exception as e:
        print(f"❌ Embedding failed: {e}")
        return []


class ChromaDBHttpClient:
    """HTTP client for ChromaDB with UUID persistence."""

    def __init__(self, host=CHROMA_HOST, port=CHROMA_PORT):
        self.base = f"http://{host}:{port}/api/v1"
        self.uuid = self._load_uuid()

    def _load_uuid(self) -> str:
        if os.path.exists(UUID_FILE):
            with open(UUID_FILE) as f:
                return f.read().strip()
        return ""

    def _save_uuid(self, uuid: str):
        with open(UUID_FILE, "w") as f:
            f.write(uuid)

    def _req(self, method, path, **kwargs):
        url = f"{self.base}{path}"
        try:
            r = requests.request(method, url, timeout=30, **kwargs)
            if r.status_code >= 400:
                print(f"⚠️  HTTP {r.status_code}: {r.text[:200]}")
            return r
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return None

    def heartbeat(self) -> bool:
        r = self._req("GET", "/heartbeat")
        return r and r.status_code == 200

    def get_or_create_collection(self, name: str):
        # Try stored UUID first
        if self.uuid:
            r = self._req("GET", f"/collections/{self.uuid}/count")
            if r and r.status_code == 200:
                return True
        # List collections (0.6.2 may return empty, so we try)
        r = self._req("GET", "/collections")
        if r and r.status_code == 200:
            for col in r.json():
                if col.get("name") == name:
                    self.uuid = col.get("id")
                    self._save_uuid(self.uuid)
                    return True
        # Create new
        r = self._req("POST", "/collections", json={
            "name": name,
            "metadata": {"hnsw:space": "cosine"},
            "get_or_create": True,
        })
        if r and r.status_code == 200:
            data = r.json()
            self.uuid = data.get("id")
            self._save_uuid(self.uuid)
            return True
        return False

    def collection_count(self) -> int:
        if not self.uuid:
            return 0
        r = self._req("GET", f"/collections/{self.uuid}/count")
        if r and r.status_code == 200:
            try:
                return int(r.text)
            except Exception:
                return 0
        return 0

    def add(self, ids: List[str], documents: List[str], embeddings: List[List[float]], metadatas: List[dict]):
        if not self.uuid:
            return False
        payload = {
            "ids": ids,
            "documents": documents,
            "embeddings": embeddings,
            "metadatas": metadatas,
        }
        r = self._req("POST", f"/collections/{self.uuid}/add", json=payload)
        return r and r.status_code == 200

    def delete(self, ids: List[str] = None, where: dict = None):
        if not self.uuid:
            return False
        payload = {}
        if ids:
            payload["ids"] = ids
        if where:
            payload["where"] = where
        if not payload:
            return False
        r = self._req("POST", f"/collections/{self.uuid}/delete", json=payload)
        return r and r.status_code == 200

    def get(self, ids: List[str] = None, where: dict = None, include: List[str] = None, limit: int = None):
        if not self.uuid:
            return None
        payload = {}
        if ids:
            payload["ids"] = ids
        if where:
            payload["where"] = where
        if include:
            payload["include"] = include
        if limit:
            payload["limit"] = limit
        r = self._req("POST", f"/collections/{self.uuid}/get", json=payload)
        if r and r.status_code == 200:
            return r.json()
        return None


def get_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def extract_metadata(filepath: str) -> Dict:
    filename = os.path.basename(filepath)
    parts = filename.replace(".md", "").split("-")
    doc_type, doc_date, doc_time = "unknown", "", ""
    if filename.startswith("STATUS"):
        doc_type, doc_date, doc_time = "status", "-".join(parts[1:4]) if len(parts) >= 4 else "", parts[4] if len(parts) > 4 else ""
    elif filename.startswith("SESSION"):
        doc_type, doc_date, doc_time = "session-notes", "-".join(parts[2:5]) if len(parts) >= 5 else "", parts[5] if len(parts) > 5 else ""
    elif filename.startswith("TEST"):
        doc_type, doc_date = "test-report", "-".join(parts[1:4]) if len(parts) >= 4 else ""
    domain = "technical-infrastructure"
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().lower()
            for d in ["bookkeeping", "market-research", "position-management", "technical-infrastructure", "wiki"]:
                if d in content:
                    domain = d
                    break
    except Exception:
        pass
    return {
        "filename": filename, "filepath": filepath, "doc_type": doc_type,
        "doc_date": doc_date, "doc_time": doc_time, "domain": domain,
        "indexed_at": datetime.now().isoformat(),
    }


def chunk_document(filepath: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict]:
    chunks = []
    metadata = extract_metadata(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    if not content.strip():
        return chunks
    start, chunk_id = 0, 0
    while start < len(content):
        end = min(start + chunk_size, len(content))
        chunk_text = content[start:end]
        meta = dict(metadata)
        meta.update({
            "chunk_id": chunk_id, "chunk_start": start, "chunk_end": end,
            "total_chunks": max(1, (len(content) + chunk_size - 1) // chunk_size),
            "file_sha256": get_sha256(filepath),
        })
        chunks.append({"id": f"{metadata['filename']}_{chunk_id}", "text": chunk_text, "metadata": meta})
        start += chunk_size - overlap
        chunk_id += 1
    return chunks


def index_documents(client: ChromaDBHttpClient, paths: List[str], incremental: bool = True):
    indexed, skipped, errors = 0, 0, 0
    for filepath in paths:
        if not os.path.isfile(filepath):
            continue
        file_hash = get_sha256(filepath)
        file_id = os.path.basename(filepath)

        # Check if already indexed
        if incremental:
            result = client.get(where={"file_sha256": file_hash}, include=[])
            if result and result.get("ids"):
                skipped += 1
                continue

        chunks = chunk_document(filepath)
        if not chunks:
            continue

        # Delete old chunks
        to_delete = []
        result = client.get(where={"filename": file_id})
        if result and result.get("ids"):
            to_delete = result["ids"]
        if to_delete:
            client.delete(ids=to_delete)

        # Generate embeddings for each chunk and batch add
        batch_ids, batch_docs, batch_embs, batch_metas = [], [], [], []
        for chunk in chunks:
            emb = get_embedding(chunk["text"])
            if not emb:
                errors += 1
                continue
            batch_ids.append(chunk["id"])
            batch_docs.append(chunk["text"])
            batch_embs.append(emb)
            batch_metas.append(chunk["metadata"])

        if batch_ids:
            success = client.add(ids=batch_ids, documents=batch_docs, embeddings=batch_embs, metadatas=batch_metas)
            if success:
                indexed += len(batch_ids)
                print(f"  ✅ {file_id}: {len(batch_ids)} chunks indexed")
            else:
                errors += len(batch_ids)
        else:
            print(f"  ⚠️  {file_id}: no embeddings generated")

    return indexed, skipped, errors


def discover_files(wiki_root: str) -> List[str]:
    paths = []
    for subdir in SUPPORTED_DIRS:
        full_dir = os.path.join(wiki_root, subdir)
        if os.path.isdir(full_dir):
            paths.extend(glob.glob(os.path.join(full_dir, "**/*.md"), recursive=True))
    plans_dir = os.path.join(wiki_root, "planning")
    if os.path.isdir(plans_dir):
        paths.extend(glob.glob(os.path.join(plans_dir, "**/*.md"), recursive=True))
    return sorted(paths)


def test_connection(client: ChromaDBHttpClient):
    if client.heartbeat():
        client.get_or_create_collection(COLLECTION_NAME)
        count = client.collection_count()
        print(f"✅ ChromaDB connection OK")
        print(f"   URL: {CHROMA_URL}")
        print(f"   Collection: {COLLECTION_NAME}")
        print(f"   UUID: {client.uuid or 'unknown'}")
        print(f"   Documents: {count}")
        return True
    print(f"❌ ChromaDB connection failed at {CHROMA_URL}")
    return False


def show_stats(client: ChromaDBHttpClient):
    count = client.collection_count()
    print(f"=== ChromaDB Collection Stats ===")
    print(f"Collection: {COLLECTION_NAME}")
    print(f"Documents: {count}")
    print(f"URL: {CHROMA_URL}")
    print(f"UUID: {client.uuid or 'unknown'}")
    if count > 0:
        result = client.get(limit=min(5, count), include=["metadatas"])
        domains = {}
        if result and result.get("metadatas"):
            for meta_list in result["metadatas"]:
                if isinstance(meta_list, list):
                    meta = meta_list[0] if meta_list else {}
                else:
                    meta = meta_list
                domain = meta.get("domain", "unknown") if meta else "unknown"
                domains[domain] = domains.get(domain, 0) + 1
        print(f"\nSample domains:")
        for domain, cnt in sorted(domains.items(), key=lambda x: -x[1]):
            print(f"  {domain}: {cnt}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Carlos' Desktop Memory Indexer")
    parser.add_argument("--index-all", action="store_true", help="Index all documents")
    parser.add_argument("--incremental", action="store_true", help="Only new/changed files")
    parser.add_argument("--file", type=str, help="Index specific file")
    parser.add_argument("--test", action="store_true", help="Test connectivity")
    parser.add_argument("--stats", action="store_true", help="Show stats")
    parser.add_argument("--use-orchestrator", action="store_true", help="Use orchestrator (127.0.0.1) for Ollama embeddings")
    args = parser.parse_args()

    global OLLAMA_URL
    if args.use_orchestrator:
        OLLAMA_URL = "http://127.0.0.1:11434"
        print("Using orchestrator (127.0.0.1:11434) for embeddings")

    client = ChromaDBHttpClient()

    if args.test:
        return test_connection(client)

    if args.stats:
        return show_stats(client)

    if args.file:
        paths = [args.file]
    else:
        paths = discover_files(WIKI_ROOT)
        print(f"Discovered {len(paths)} documents to index")

    incremental = args.incremental or not args.index_all
    mode = "incremental" if incremental else "full"

    print(f"\nIndexing mode: {mode}")
    print(f"Collection: {COLLECTION_NAME}")
    print(f"ChromaDB: {CHROMA_URL}")
    print(f"Ollama: {OLLAMA_URL} (model: {EMBEDDING_MODEL})")
    print(f"Documents: {len(paths)}\n")

    client.get_or_create_collection(COLLECTION_NAME)

    indexed, skipped, errors = index_documents(client, paths, incremental=incremental)

    print(f"\n=== Results ===")
    print(f"Indexed:  {indexed} chunks")
    print(f"Skipped:  {skipped} (unchanged)")
    print(f"Errors:   {errors} (embedding failures)")
    print(f"Total in collection: {client.collection_count()}")

    return True


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
