# TI-033: Lab Node SSHFS Mount Capability

**Issue Home:** [0-ISSUE.md](./0-ISSUE.md)
**Status:** ✅ **COMPLETE** — 2026-05-14
**Priority:** 🟡 **MEDIUM**

---

### TI-033: Lab Node SSHFS Mount Capability
**Created:** 2026-05-05
**Completed:** 2026-05-14
**Status:** ✅ **COMPLETE**
**Priority:** 🟡 **MEDIUM**
**Rationale:** Mount orchestrator workspace on lab nodes via SSHFS for parallel work distribution. Scripts exist (`mount-lab-node.sh`, `unmount-lab-node.sh`, `playbooks/mount-unmount-workspace.yml`). **sshfs installed on all 7 nodes 2026-05-05.** Mounting requires reverse SSH (lab → orchestrator) which is blocked by Mac Remote Login setting.

**Prerequisites:**
- [x] Lab nodes must install `sshfs` and `fuse` packages — **COMPLETED** 2026-05-05 via parallel SSH ad-hoc
- [x] Orchestrator must have passwordless SSH FROM lab nodes back to orchestrator (reverse direction)
- [x] SSH key propagation required
- [x] **VERIFY:** `ssh -o BatchMode=yes 192.168.0.184 echo ok` from fnet1 succeeds

**Deliverables:**
- [x] sshfs installed on fnet1–fnet7 via `sudo apt-get install -y sshfs fuse3`
- [x] Enable Mac Remote Login (System Preferences → Sharing → Remote Login) — **VERIFIED WORKING 2026-05-14**
- [x] Ansible playbook: `playbooks/configure-reverse-ssh.yml` — **CREATED 2026-05-05**
- [x] Mount/unmount helper scripts (deployed via playbook)
- [x] Documentation: `wiki/guides/lab-node-mount-guide.md` — **CREATED 2026-05-05**
- [x] **DONE:** Verify SSH connectivity from lab node: `ssh fnet1 "ssh -o BatchMode=yes 192.168.0.184 echo ok"` — **PASSES on all 7 nodes**
- [x] **DONE:** Test mount on fnet1–fnet7: All 7 nodes mounted successfully 2026-05-14

**Resolution Notes (2026-05-14):**
- Root cause of blocker: orchestrator IP had changed from 192.168.0.140 → 192.168.0.184
- 192.168.0.140 now belongs to a different device on the network (ARP confirmed)
- Generated SSH keys on fnet2–fnet5 (fnet1, fnet6, fnet7 already had keys)
- Added all 7 lab node public keys to orchestrator's `~/.ssh/authorized_keys`
- Added `192.168.0.184 mac-orchestrator` to `/etc/hosts` on all 7 lab nodes
- Fixed mount script: removed unsupported FUSE options (`defer_permissions`, `volname`)
- All 7 nodes mount at `/mnt/trading-desk` → `/Users/friasc/Dropbox/workshop`

**Blocker Status (2026-05-05):**
```
# Test from orchestrator to itself
ssh -o BatchMode=yes 192.168.0.140 echo ok
# → Operation timed out (port 22 not responding)

# Ping succeeds (network OK)
ping 192.168.0.140
# → 64 bytes, ~7ms latency
```
**Next Action:** Verify macOS Remote Login is actively enabled (not just highlighted). Check System Preferences → Sharing → Remote Login checkbox is ticked. May require 1-2 min startup or firewall exception.

**Estimated Effort:** ~20 minutes (resolved)
**Use Cases:**
1. ✅ Distribute wiki link fixing to fnet3–fnet6 in parallel
2. ✅ Lab nodes write session notes directly without SCP  
3. ✅ Real-time performance log streaming

---

## ☑️ Complete

---

## Navigation

| Need | Location |
|------|----------|
| Back to backlog | [../BACKLOG.md](../BACKLOG.md) |
