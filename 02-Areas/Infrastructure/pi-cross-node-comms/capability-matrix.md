# Fleet Node Capability Matrix

**Created:** 2026-05-26  
**Source:** Empirical testing through pi-cross-node-comms Phase 5 E2E validation  
**Status:** Active — update as fleet evolves

---

## Capability Dimensions

Each fleet peer is scored across these dimensions based on empirical testing:

| Dimension | Test Method | Pass Criteria |
|-----------|------------|---------------|
| **simple-bash** | `ls`, `echo`, file checks | Response within 30s |
| **file-read** | `read` tool on text/image files | Returns content within 30s |
| **file-write** | `write` tool creating files | File created, no errors |
| **vision** | `read` on image → multimodal-proxy → vision_proxy_description | Fence returned within 120s |
| **video-extract** | `ffmpeg` frame extraction | Output file created |
| **code-gen** | `write` tool creating test files | File created with valid syntax |
| **plan-update** | `edit` tool on markdown files | Changes applied correctly |
| **complex** | Multi-step tasks (read → write → verify) | All steps complete within 60s |

---

## Peer Capability Matrix

### Same-Machine Peers (macOS orchestrator)

| Peer | Model | simple-bash | file-read | vision | video-extract | code-gen | plan-update | complex |
|------|-------|:-----------:|:---------:|:------:|:------------:|:--------:|:-----------:|:-------:|
| **agent-RZDZMM** | qwen3.5:397b-c | ✅ | ✅ | ✅ | ✅ | ❓ | ❓ | ❓ |
| **agent-3VN9XS** | gemma4:31b-clo | ✅ | ✅ | ✅ | ❓ | ❌ | ❌ | ❌ |
| **agent-RJMTWQ** | gemma4:31b-clo | ✅ | ❓ | ❓ | ❓ | ❌ | ✅ | ❌ |
| **agent-MVV25X** | deepseek-v4-pr | ❌ | ❌ | ❌ | ❓ | ❌ | ❌ | ❌ |
| **agent-NFDTGH** | deepseek-v4-pr | ❌ | ❌ | ❌ | ❓ | ❌ | ❌ | ❌ |
| **agent-HPQ8AP** | qwen3.5:397b-c | ❌ | ❌ | ❌ | ❓ | ❌ | ❌ | ❌ |
| **agent-29XM28** | qwen3.5:397b-c | ❌ | ❌ | ❌ | ❓ | ❌ | ❌ | ❌ |

### Lab Fleet Nodes (fnet1-7, systemd+tmux)

| Node | Model | Status | Notes |
|------|-------|--------|-------|
| fnet1 | qwen3.5:4b + qwen3:8b + gemma4:e4b | ✅ Online | 15Gi RAM, 4 cores |
| fnet3 | qwen3.5:4b + qwen3:8b + gemma4:e4b | ✅ Online | 31Gi RAM, 12 cores |
| fnet4 | qwen3.5:4b + qwen3:8b + gemma4:e4b | ✅ Online | 31Gi RAM, 12 cores |
| fnet5 | qwen3.5:4b + qwen3:8b + gemma4:e4b | ✅ Online | 31Gi RAM, 12 cores |
| fnet6 | qwen3.5:4b + qwen3:8b + gemma4:e4b | ✅ Online | 31Gi RAM, 12 cores |
| fnet7 | qwen3.5:4b + qwen3:8b + gemma4:e4b | ✅ Online | 15Gi RAM, 12 cores |

**Lab fleet capability:** Untested for video. All lab nodes have ffmpeg via Ansible but haven't been validated for video E2E. Same-machine peers are the validated baseline.

---

## Findings from Phase 5 Testing

### 1. Decomposition is essential for video tasks

Video E2E must be decomposed into atomic sub-tasks:
```
Create video → Extract frame (bash, <5s) → Read frame (vision, <30s)
```

A single "analyze this video" task times out. The decomposed pipeline succeeds.

### 2. Simple tasks succeed reliably; complex tasks don't

| Complexity | Success Rate | Example |
|-----------|:-----------:|---------|
| Simple bash/read | ~60% (3/5 peers) | `ls`, `cat`, `read` |
| Plan updates | ~40% (2/5 peers) | `edit` on markdown |
| Code generation | ~0% (0/5 peers) | `write` test files |
| Vision analysis | ~40% (2/5 peers) | `read` image + proxy |

### 3. Same-machine peers have model-dependent reliability

- **qwen3.5:397b-c** (agent-RZDZMM): Most reliable, handles bash + vision + video
- **gemma4:31b-clo** (agent-3VN9XS, agent-RJMTWQ): Reliable for simple tasks
- **deepseek-v4-pr** (agent-MVV25X, agent-NFDTGH): Unreliable across all categories

### 4. All same-machine peers share the orchestrator's filesystem

This means file-based coordination works (write file → tell peer to read it) without network transfer. Video frames can be extracted locally on the orchestrator and read by fleet peers.

---

## Routing Implications

1. **Video tasks:** Always decompose. Never send "analyze this video" as a single task.
2. **Code generation:** Don't route to fleet. Use Tier 3 subagents or orchestrator.
3. **Simple reads/bash:** Route to agent-RZDZMM or agent-3VN9XS.
4. **Vision analysis:** Route to agent-RZDZMM or agent-3VN9XS (both have multimodal-proxy loaded).
5. **Lab fleet (fnet1-7):** Untested for video/vision. Needs validation.

---

*Cross-reference: pi-multimodal-proxy Phase 4 E2E, pi-cross-node-comms Phase 5.3, node-router DECOMPOSITION.md*
