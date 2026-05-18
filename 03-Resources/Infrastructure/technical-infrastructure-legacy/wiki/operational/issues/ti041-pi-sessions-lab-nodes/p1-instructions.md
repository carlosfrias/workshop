# TI-041 Phase 1 — Install pi CLI on fnet1–fnet7

## Goal
Install pi CLI on all 7 lab nodes and verify basic connectivity.

## Steps

### 1. Check if Node.js/npm exists on each lab node
```bash
for node in fnet1 fnet2 fnet3 fnet4 fnet5 fnet6 fnet7; do
  echo "=== $node ==="
  ssh "$node" "which node && node --version && which npm && npm --version" 2>/dev/null || echo "Node.js not installed"
done
```

### 2. Install Node.js if missing (Ubuntu)
```bash
for node in fnet1 fnet2 fnet3 fnet4 fnet5 fnet6 fnet7; do
  ssh "$node" "sudo apt-get update && sudo apt-get install -y nodejs npm" 2>/dev/null || echo "Install failed on $node"
done
```

### 3. Install pi CLI
```bash
for node in fnet1 fnet2 fnet3 fnet4 fnet5 fnet6 fnet7; do
  ssh "$node" "npm install -g @earendil-works/pi-coding-agent 2>/dev/null || echo 'npm install failed, trying alternative'" 2>/dev/null
done
```

### 4. Verify installation
```bash
for node in fnet1 fnet2 fnet3 fnet4 fnet5 fnet6 fnet7; do
  ssh "$node" "which pi && pi --version" 2>/dev/null || echo "pi not found on $node"
done
```

### 5. Report evidence
For each node, report:
- Node.js version (if installed)
- pi CLI version (if installed)
- Any errors

## Expected
- pi CLI available on all reachable nodes
- Errors documented for any unreachable nodes
