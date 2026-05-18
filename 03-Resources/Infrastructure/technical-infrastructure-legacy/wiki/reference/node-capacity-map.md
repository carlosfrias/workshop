# Node Capacity Map
**Generated:** 2026-05-02 by fnet3/qwen3:8b (auto-distributed)  
**Updated:** 2026-05-05 after fnet1 model deployment  
**Status:** Living document — update after hardware changes

## Per-Node Hardware

| Node | CPU | Cores | RAM | Safe Capacity | IP | Installed Models |
|------|-----|-------|-----|--------------|-----|-----------------|
| fnet1 | Intel i5-6400 | 4 | 15GB | 12.5GB | 192.168.0.141 | qwen3.5:4b, qwen3:8b |
| fnet2 | Intel i5-6400 | 4 | 15GB | 12.5GB | 192.168.0.142 | qwen3.5:4b, qwen3:8b |
| fnet3 | Intel i7-10710U | 12 | 31GB | 27.0GB | 192.168.0.143 | qwen3.5:4b, qwen3:8b, gemma4:e4b |
| fnet4 | Intel i7-10710U | 12 | 31GB | 27.0GB | 192.168.0.144 | qwen3.5:4b, qwen3:8b, gemma4:e4b |
| fnet5 | Intel i7-10710U | 12 | 31GB | 27.0GB | 192.168.0.145 | qwen3.5:4b, qwen3:8b, gemma4:e4b |
| fnet6 | Intel i7-10710U | 12 | 31GB | 27.0GB | 192.168.0.146 | qwen3.5:4b, qwen3:8b, gemma4:e4b |
| fnet7 | Intel i5-6400 | 4 | 15GB | 12.5GB | 192.168.0.147 | qwen3.5:4b, qwen3:8b |
| Mac (Orchestrator) | Apple M4 Pro | 14 | 24GB | — | 192.168.0.140 | qwen3.5:4b, qwen3:8b, gemma4:e4b, nomic-embed-text |

## Per-Model Specs

| Model | Size | Context | Tokens/sec | Capabilities | Min RAM |
|-------|------|---------|-----------|--------------|---------|
| qwen3.5:4b | 3.4GB | 131,072 | ~3.5–4.6 | vision, tools, reasoning | 8GB |
| qwen3:8b | 5.2GB | 32,768 | ~3.3–4.8 | tools, reasoning | 14GB |
| gemma4:e4b | 9.6GB | 131,072 | ~5.4–6.5 | vision, tools, reasoning | 22GB |

## Routing Decision Matrix

| Complexity | Vision Required | Best Node | Best Model | Max Tokens |
|------------|----------------|-----------|-----------|------------|
| trivial/simple | No | fnet1/2/7 | qwen3.5:4b | 111,411 |
| medium | No | fnet3-6 | qwen3:8b | 27,852 |
| medium/hard | Yes | fnet3-6 | gemma4:e4b | 111,411 |
| hard | No | fnet3-6 | qwen3:8b | 27,852 |
| exceeds local | Any | cloud | qwen3.5:397b-cloud | 222,822 |

## Notes
- Safe capacity = RAM - 3GB OS overhead - 20% buffer
- Max tokens = context_window × 0.85 (hard limit)
- All nodes run Ubuntu 24.04 with ollama 0.22.x–0.23.x
- Task worker timer: 15s interval
- fnet1 models deployed 2026-05-05 (qwen3.5:4b + qwen3:8b, 8.6GB total)
