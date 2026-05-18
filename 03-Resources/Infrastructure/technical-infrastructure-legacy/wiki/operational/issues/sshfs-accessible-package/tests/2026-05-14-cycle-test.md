# Test — Full Mount/Unmount Cycle

**Date:** 2026-05-14 13:20 ET
**Tester:** AI Agent (orchestrator) + fnet6 (lab node for evidence gathering)
**Issue:** [sshfs-accessible-package](../0-ISSUE.md)

---

## Test: Full Mount/Unmount Cycle

### Procedure

```bash
cd technical-infrastructure/packages/sshfs-accessible

# 1. Unmount all
./scripts/unmount-all.sh

# 2. Verify unmounted
./scripts/verify-mounts.sh

# 3. Remount all
./scripts/mount-all.sh

# 4. Final verify (JSON)
./scripts/verify-mounts.sh --json
```

### Results

| Step | fnet1 | fnet2 | fnet3 | fnet4 | fnet5 | fnet6 | fnet7 |
|------|-------|-------|-------|-------|-------|-------|-------|
| Unmount | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| Verify unmounted | NOT MOUNTED | NOT MOUNTED | NOT MOUNTED | NOT MOUNTED | NOT MOUNTED | NOT MOUNTED | NOT MOUNTED |
| Remount | PASS | PASS | PASS | PASS | PASS | PASS | PASS* |
| Final verify | mounted | mounted | mounted | mounted | mounted | mounted | mounted |

* fnet7 mount succeeded but output timed out; individually retested — confirmed mounted

### JSON Evidence

```json
{
  "timestamp": "2026-05-14T17:39:09Z",
  "orchestrator": "mac-orchestrator",
  "nodes": {
    "fnet1": {"status": "mounted", "mount_point": "/mnt/trading-desk"},
    "fnet2": {"status": "mounted", "mount_point": "/mnt/trading-desk"},
    "fnet3": {"status": "mounted", "mount_point": "/mnt/trading-desk"},
    "fnet4": {"status": "mounted", "mount_point": "/mnt/trading-desk"},
    "fnet5": {"status": "mounted", "mount_point": "/mnt/trading-desk"},
    "fnet6": {"status": "mounted", "mount_point": "/mnt/trading-desk"},
    "fnet7": {"status": "mounted", "mount_point": "/mnt/trading-desk"}
  }
}
```

### Idempotency Test

Running `mount-all.sh` on already-mounted nodes correctly detects and skips them:
```
fnet1  → already mounted
fnet2  → already mounted
...
```

### Verdict: PASS
