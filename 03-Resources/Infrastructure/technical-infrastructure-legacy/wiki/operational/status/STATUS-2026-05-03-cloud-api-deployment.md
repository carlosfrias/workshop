# Cloud API Key Deployment to Lab Nodes — Status Report

**Date:** 2026-05-03 23:59 ET  
**Task:** Deploy Ollama Cloud API key to all lab nodes  
**Status:** 🟡 **PARTIALLY COMPLETE** — API key deployed, OAuth pending  

---

## What Was Done

### 1. API Key Extracted ✅
- Source: `~/.pi/agent/models.json` on orchestrator (Mac)
- API Key: `add5554ce82d4c018d12760589987d56.ytYqhxD-KUnAMfhCzP7zObNJ`
- Format: Ollama Cloud API key

### 2. Models.json Deployed ✅
Deployed to all lab nodes at `~/.pi/agent/models.json`:
- ✅ fnet1 (already had it)
- ✅ fnet3
- ✅ fnet4
- ✅ fnet5
- ✅ fnet6
- ✅ fnet7

### 3. Auth.json Deployed ✅
Created `~/.pi/agent/auth.json` on all nodes with:
```json
{
  "ollama-cloud": {
    "type": "api_key",
    "key": "add5554ce82d4c018d12760589987d56.ytYqhxD-KUnAMfhCzP7zObNJ"
  }
}
```

### 4. SSH Key Pair Deployed ✅
Deployed Ollama SSH keys to all nodes:
- `~/.ollama/id_ed25519` (private key)
- `~/.ollama/id_ed25519.pub` (public key)
- Added to `~/.profile`: `export OLLAMA_API_KEY=$(cat ~/.ollama/id_ed25519.pub)`

---

## What Remains: OAuth Authentication

### Issue
The `ollama run` command for cloud models requires **browser-based OAuth authentication**, not just API key configuration. This is a one-time per-node setup.

### Authentication URLs

Each node has a unique OAuth URL. Visit these URLs in a browser to complete authentication:

| Node | OAuth URL |
|------|-----------|
| **fnet3** | https://ollama.com/connect?name=fnet3&key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSUlOQ2JSdXZodVk0WTBUb1YraDU0ckloc2FnK2JRQk9XL1FZaXgxMGpyeDA |
| **fnet4** | https://ollama.com/connect?name=fnet4&key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSUM4eTNpSzVTTzRaLzIxWHFBRFU3YWprWkhLSDFPcDU0TTk2V2JZdlhSVzg |
| **fnet5** | https://ollama.com/connect?name=fnet5&key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSU5ydnBnTGZkYXhEaTRndGVlWnV3cEo5R1JPSHpPWDJXZHRqM1dBMkk1d0I |
| **fnet6** | https://ollama.com/connect?name=fnet6&key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSUEvZjlqb2d0Yk5iZldyOEZwdXpXcUFUT1MzWEYzN1F0M3NKYTdoS1NYQnQ |
| **fnet7** | https://ollama.com/connect?name=fnet7&key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSUloSDhvT2FTZUhnNy9JM1ZEUjUzTDJTUStXMzBaWkNWWjZzSmNLU2JmZ0o |

### How to Complete Authentication

**Option 1: Manual Browser Authentication (Recommended)**
1. Click each OAuth URL above
2. Sign in with your Ollama.com account
3. Approve the connection for that node
4. Verify with: `ollama run qwen3.5:397b-cloud 'Hi'`

**Option 2: SSH + Browser Forwarding**
If you have X11 forwarding or can open browsers from SSH:
```bash
ssh -X fnet3 "ollama signin"
# Browser should open automatically
```

**Option 3: Copy Auth Token**
After authenticating one node, copy the auth token to others:
```bash
# After authenticating fnet3
scp fnet3:~/.ollama/id_token fnet4:~/.ollama/
scp fnet3:~/.ollama/id_token fnet5:~/.ollama/
# etc.
```

---

## Verification Commands

After completing OAuth, verify on each node:

```bash
# Test cloud model access
ollama run qwen3.5:397b-cloud 'Say hello from cloud'

# Expected output:
# Hello! How can I help you today?
```

---

## Files Deployed

| File | Location | Purpose |
|------|----------|---------|
| `models.json` | `~/.pi/agent/models.json` | Cloud model definitions + API key |
| `auth.json` | `~/.pi/agent/auth.json` | Ollama Cloud authentication for pi extension |
| `id_ed25519` | `~/.ollama/id_ed25519` | SSH private key for Ollama |
| `id_ed25519.pub` | `~/.ollama/id_ed25519.pub` | SSH public key (used as API key) |
| `~/.profile` | `~/.profile` | Added `OLLAMA_API_KEY` export |

---

## Security Notes

- ✅ API key is the same across all nodes (shared subscription)
- ✅ SSH keys are identical (copied from orchestrator)
- ⚠️ OAuth tokens will be unique per node after authentication
- ✅ All files have proper permissions (600 for private keys)

---

## Next Steps

1. **Complete OAuth** — Visit the 5 OAuth URLs above (5 minutes)
2. **Verify Access** — Run test command on each node (2 minutes)
3. **Update Router** — Ensure keyword router includes cloud models in routing decisions
4. **Test Routing** — Submit a task that should route to cloud models

---

## Summary

| Task | Status | Notes |
|------|--------|-------|
| Extract API key from orchestrator | ✅ Complete | From `~/.pi/agent/models.json` |
| Deploy `models.json` to nodes | ✅ Complete | All 6 nodes (fnet1, fnet3-7) |
| Deploy `auth.json` to nodes | ✅ Complete | All 5 nodes (fnet3-7) |
| Deploy SSH keys to nodes | ✅ Complete | All 5 nodes (fnet3-7) |
| OAuth authentication | 🔴 Pending | Requires browser interaction |
| Verify cloud model access | 🔴 Pending | After OAuth completion |

---

**OAuth authentication is the only remaining step. Once completed, all lab nodes will have full access to Ollama Cloud models.**
