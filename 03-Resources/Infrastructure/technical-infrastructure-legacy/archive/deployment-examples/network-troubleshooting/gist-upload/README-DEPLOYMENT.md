# Network Troubleshooting - Single-Command Deployment

**Pattern:** Automated deployment via `curl | bash`  
**Gist:** https://gist.github.com/carlosfrias/0c517214489cb78c0484ca661f3d8463

---

## ⚡ Quick Start

```bash
curl -L https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/deploy.sh | bash -s -- --api-key YOUR_OLLAMA_CLOUD_API_KEY
```

**Get your API key:** https://ollama.com/settings/keys

---

## 📋 What This Does

The deployment script handles everything automatically:

1. ✅ Downloads diagnostic scripts
2. ✅ Configures pi with local + cloud models
3. ✅ Tests pi is working
4. ✅ **Pauses and prompts you to disconnect tether** (critical!)
5. ✅ Verifies tether is disconnected
6. ✅ Runs diagnostics WITHOUT tether
7. ✅ Displays output to copy/paste to cloud agent

---

## 🔑 Important Notes

### API Key
- **Required:** Pass via `--api-key YOUR_KEY` argument
- **Stored in:** `~/.pi/agent/models.json` (embedded, not env var)
- **Used by:** pi agent for cloud model access

### Configuration Files
| File | Location | Purpose |
|------|----------|---------|
| `models.json` | `~/.pi/agent/models.json` | ALL config (providers + models) |
| `providers.json` | **DOES NOT EXIST** | Not used - don't create |
| Agent definitions | `~/.pi/agent/agents/` | Custom agents |

### Model Names
- **Local:** `qwen3.5:4b`
- **Cloud:** `qwen3.5:cloud`
- **Both in same provider:** `ollama`

### Tether Disconnect
**CRITICAL:** The script will pause and prompt you to disconnect the phone tether. This is essential because:
- Diagnostics must run WITHOUT tether to see the real ethernet problem
- If tether is connected, it masks the ethernet issue
- The script verifies tether is gone before running diagnostics

---

## 🚀 Workflow

### Phase 1: Deploy (Tether Connected, ~5 min)

```bash
# On target node:
curl -L https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/deploy.sh | bash -s -- --api-key YOUR_KEY
```

The script will:
- Download all scripts
- Configure pi
- Test models
- **Pause and prompt you to disconnect tether**

### Phase 2: Diagnostics (No Tether, ~3 min)

After you disconnect tether and press ENTER:
- Script verifies tether is gone
- Runs hardware detection
- Runs network diagnostics
- Displays output for you to copy

### Phase 3: Cloud Analysis (On Your Mac)

1. Copy all diagnostic output (from `=== GATEWAY PING ===` onwards)
2. Paste to cloud agent session on your Mac
3. Cloud agent analyzes and provides fix commands

### Phase 4: Apply Fixes (On Target Node, ~10 min)

```bash
# Run fix commands provided by cloud agent
~/network-troubleshooting-bundle/apply-fix.sh <fix-number> [options]

# Verify
~/network-troubleshooting-bundle/verify.sh

# Check status
cat /tmp/node-ready.txt
```

### Phase 5: Final Verification (Tether Reconnected, ~2 min)

```bash
# Reconnect tether briefly
# Paste verification log to cloud agent
cat /tmp/network-verify-*.log

# Wait for confirmation
```

---

## 📁 Files in This Gist

| File | Purpose |
|------|---------|
| `deploy.sh` | **Main deployment script** (use this!) |
| `install-ollama.sh` | Ollama installer |
| `detect-hardware.sh` | Hardware detection |
| `benchmark-model.sh` | Model benchmark |
| `diagnose.sh` | Network diagnostics |
| `apply-fix.sh` | Fix application |
| `verify.sh` | Verification |
| `technical-infrastructure.md` | Local agent definition |
| `verifier.md` | Cloud verifier definition |
| `fix-models.sh` | Manual config fix (legacy) |

---

## ⏱️ Time Budget Per Node

| Phase | Duration | Tether |
|-------|----------|--------|
| Deploy | 3-5 min | ✅ |
| Diagnostics | 2-3 min | ❌ |
| Cloud Analysis | 2-3 min | ✅ (paste output) |
| Apply Fixes | 5-10 min | ❌ |
| Verification | 2-3 min | ❌ |
| Final Check | 1-2 min | ✅ |
| **Total Tether** | **~8-10 min** | |

---

## ✅ Success Criteria

- [ ] Deploy script completes without errors
- [ ] pi models list shows qwen3.5:4b and qwen3.5:cloud
- [ ] Tether disconnected before diagnostics
- [ ] Diagnostic output copied and pasted to cloud agent
- [ ] Fix commands applied successfully
- [ ] `/tmp/node-ready.txt` shows: `COMPLETE`

---

## 🔄 For Future Troubleshooting Sessions

1. Create new Gist with updated scripts
2. Update deploy.sh with new Gist URL
3. Use same single-command pattern:
   ```bash
   curl -L <NEW_GIST_URL>/deploy.sh | bash -s -- --api-key YOUR_KEY
   ```

---

## 🐛 Common Issues

### "No models available" error
- **Cause:** models.json schema is wrong
- **Fix:** Run `fix-models.sh` or re-run `deploy.sh`
- **Prevention:** Use exact Mac schema (single provider, models array)

### Tether still detected after disconnect
- **Cause:** Phone still broadcasting tether
- **Fix:** Fully disable tethering on phone, unplug USB
- **Verify:** `ip -br addr show` - no `enx*` interfaces

### Diagnostics show internet working
- **Cause:** Tether still connected
- **Fix:** Disconnect tether, re-run diagnostics
- **Verify:** `ip route | grep default` - should only show ethernet gateway

---

**Next:** Continue with Node 2 diagnostics and paste output to cloud agent.
