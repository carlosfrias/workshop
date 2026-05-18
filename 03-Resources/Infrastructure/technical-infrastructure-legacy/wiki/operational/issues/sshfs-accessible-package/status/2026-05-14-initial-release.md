# Status — Initial Release

**Timestamp:** 2026-05-14 13:45 ET
**Issue:** [sshfs-accessible-package](../0-ISSUE.md)
**Phase:** Complete — Initial Release v1.0.0
**Written via:** fnet3 SSHFS mount → orchestrator workspace

---

## Component Status

| Component | Status | Notes |
|-----------|--------|-------|
| `package.json` | Done | Pi manifest with `pi.skills` |
| `SKILL.md` | Done | Agent Skills compliant |
| `nodes.json` | Done | 1 orchestrator + 7 lab nodes |
| `mount-all.sh` | Done | Tested: fresh mount + idempotent re-mount |
| `unmount-all.sh` | Done | Tested: unmount all 7 nodes |
| `verify-mounts.sh` | Done | Human + JSON output |
| `mount-helpers.sh` | Done | Portable bash, no bash ≥4 features |
| `README.md` | Done | Quick start instructions |
| `0-ISSUE.md` | Done | Canonical issue definition |
| Session notes | Done | Package creation session |
| Prompt capture | Done | User request verbatim |
| Test evidence | Done | Full mount/unmount cycle |

## Known Limitations

1. **SSHFS 3.7.3** on lab nodes — some newer FUSE options unsupported
2. **Parallel mount timeout** — mounting all 7 nodes simultaneously may timeout; use smaller batches or sequential mode
3. **No systemd auto-mount** — future enhancement (persist mounts across reboots)
4. **Private repo not yet created on GitHub** — package functional locally and installable via local path

## Health Check

```bash
./verify-mounts.sh --json
# → All 7 nodes: {"status": "mounted"}
```

## Dependencies Resolved

- [x] TI-033 (SSHFS mount capability) — completed earlier this session
- [x] SSH keys generated on fnet2–fnet5
- [x] All 7 keys in orchestrator authorized_keys
- [x] `mac-orchestrator` hostname resolvable on all lab nodes
- [x] Host keys trusted on all lab nodes
