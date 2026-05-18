# TDOF-001: Vector Memory with RAG Retrieval

**Issue Home:** [0-ISSUE.md](./0-ISSUE.md)
**Status:** TBD
**Priority:** TBD

---

### TDOF-001: Vector Memory with RAG Retrieval
**Created:** 2026-05-04  
**Status:** ✅ **COMPLETE** — ChromaDB deployed, Ollama embeddings integrated, RAG retrieval functional  
**Priority:** 🔴 **CRITICAL** — Biggest gap between "stateless chatbot" and "agentic system"  
**Rationale:** AgenticOS design specifies vector-backed long-term storage with RAG retrieval. Currently Trading Desk has file-based memory (session notes, status docs) but no semantic search or retrieval augmentation.  

**Deliverables:**
- [x] ChromaDB deployed on fnet3 (31GB RAM, **v0.6.2**, port 8000) — *0.6.3 had async bug in collections endpoint*
- [x] Ollama `nomic-embed-text` on fnet3 for 768-dim embeddings
- [x] Embedding pipeline (`chromadb-embedding.py`) with Ollama integration, incremental updates
- [x] RAG retrieval API (`rag-retrieve.py`) with domain/date filtering — **VERIFIED WORKING**
- [x] Performance logger updated with `log_retrieval()`
- [x] Plan document created
- [x] Initial index run completed (609 chunks across 76 documents)
- [ ] Integration with decomposer tested

**Verification:**
```bash
# ChromaDB health
curl http://192.168.0.143:8000/api/v1/heartbeat  # → 200

# Index documents (generates embeddings via Ollama)
python3 technical-infrastructure/scripts/chromadb-embedding.py --index-all

# Test RAG retrieval
python3 technical-infrastructure/scripts/rag-retrieve.py "fnet7 performance" --top-k 5
```

**Estimated Effort:** 4-6 hours
**Blocked By:** None

---

## Navigation

| Need | Location |
|------|----------|
| Back to backlog | [../BACKLOG.md](../BACKLOG.md) |
