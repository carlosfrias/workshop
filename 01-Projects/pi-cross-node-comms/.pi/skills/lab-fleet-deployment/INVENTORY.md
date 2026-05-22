---
section_id: inventory
size_estimate: ~2.2KB
lod_level: Low
purpose: Node inventory, IPs, roles, and models for the 7-node fnet lab fleet.
---

# Fleet Inventory

## [S-TIGHT]

Node inventory with IPs, roles, Ollama models, and pi versions for the 7-node fnet lab fleet.

[LOD: Low] *Always load. Core reference for node addressing and capabilities.*

## Topology

```mermaid
graph TB
    HUB["Hub: fnet2 .142<br/>Bun :8080"] --> N1["fnet1 .141"]
    HUB --> N3["fnet3 .143"]
    HUB --> N4["fnet4 .144"]
    HUB --> N5["fnet5 .145"]
    HUB --> N6["fnet6 .146"]
    HUB --> N7["fnet7 .147"]

    style HUB fill:#36F9F6,stroke:#333,color:#000
```

## Node Table

| Node | IP | Role | Ollama | pi | Agent |
|------|-----|------|--------|-----|-------|
| fnet2 | 192.168.0.142 | Hub host + worker | qwen3.5:4b, qwen3:8b, gemma4:e4b | 0.74.0 | ✅ |
| fnet1 | 192.168.0.141 | Worker | qwen3.5:4b, qwen3:8b, gemma4:e4b | 0.74.0 | ✅ |
| fnet3 | 192.168.0.143 | Worker | qwen3.5:4b, qwen3:8b, gemma4:e4b | 0.74.0 | ✅ |
| fnet4 | 192.168.0.144 | Worker | qwen3.5:4b, qwen3:8b, gemma4:e4b | 0.74.0 | ✅ |
| fnet5 | 192.168.0.145 | Worker | qwen3.5:4b, qwen3:8b, gemma4:e4b | 0.74.0 | ✅ |
| fnet6 | 192.168.0.146 | Worker | qwen3.5:4b, qwen3:8b, gemma4:e4b | 0.74.0 | ✅ |
| fnet7 | 192.168.0.147 | Worker | qwen3.5:4b, qwen3:8b, gemma4:e4b | 0.74.0 | ✅ |

## Quick Ref

- **Hub:** fnet2 (192.168.0.142:8080)
- **Workers:** fnet1, fnet3–fnet7 (5 typically online)
- **All nodes:** Same Ollama models, same pi version (0.74.0)

---

*See also: [CONNECTION.md](CONNECTION.md) for connect parameters, [MONITORING.md](MONITORING.md) for status checks.*