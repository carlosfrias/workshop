#!/bin/bash
# check-model-tier.sh — Detect context window tier for skill routing
# Usage: check-model-tier.sh [model-id]
#   Without args: guesses from pi config or defaults to first model
#   With args:    checks specific model
# Output: "linear" or "decomposed"
# Exit codes: 0=success, 1=error

MODELS_FILE="${HOME}/.pi/agent/models.json"
ROUTER_FILE="${HOME}/.pi/agent/model-router.json"

# ── Read threshold from model-router ──
# Default to 32000 if router file missing
THRESHOLD=32000
if [ -f "$ROUTER_FILE" ]; then
    # Extract largeContextThreshold value (handles both int and float)
    THRESHOLD=$(python3 -c "
import json, sys
with open('$ROUTER_FILE') as f:
    cfg = json.load(f)
print(int(cfg.get('largeContextThreshold', 32000)))
" 2>/dev/null || echo 32000)
fi

# ── Determine model ID ──
MODEL_ID=""
if [ -n "$1" ]; then
    MODEL_ID="$1"
else
    # Try pi config first
    if [ -f "${HOME}/.pi/config.json" ]; then
        MODEL_ID=$(python3 -c "
import json
with open('${HOME}/.pi/config.json') as f:
    cfg = json.load(f)
print(cfg.get('model', ''))
" 2>/dev/null)
    fi
    # Fallback: try model-router default profile
    if [ -z "$MODEL_ID" ] && [ -f "$ROUTER_FILE" ]; then
        MODEL_ID=$(python3 -c "
import json
with open('$ROUTER_FILE') as f:
    cfg = json.load(f)
profile = cfg.get('defaultProfile', 'auto')
profiles = cfg.get('profiles', {})
auto = profiles.get(profile, {})
# Get high-tier model as default
high = auto.get('high', {})
print(high.get('model', ''))
" 2>/dev/null)
    fi
    # Final fallback
    if [ -z "$MODEL_ID" ]; then
        echo "decomposed"  # Assume high-capacity by default
        exit 0
    fi
fi

# ── Look up context window ──
CTX_WINDOW=$(python3 -c "
import json
model_id = '$MODEL_ID'
with open('$MODELS_FILE') as f:
    cfg = json.load(f)

# Search all providers for this model
for provider in cfg.get('providers', {}).values():
    for model in provider.get('models', []):
        if model.get('id') == model_id:
            print(model.get('contextWindow', 32000))
            sys.exit(0)
# Not found — assume high capacity
print(32000)
" 2>/dev/null)

# ── Route ──
CTX_WINDOW=${CTX_WINDOW:-32000}

if [ "$CTX_WINDOW" -lt "$THRESHOLD" ]; then
    echo "linear"
else
    echo "decomposed"
fi
