# Decomposition: Block Device "Busy" Despite No Visible Processes

**Problem:** `wipefs`, `partx`, `pvcreate`, or similar block device operations fail with "Device or resource busy", but `lsof`, `fuser`, and `lslocks` show no holders and no visible processes are using the device.

**Root Cause:** Systemd services with `ProtectSystem` and `PrivateTmp` directives create **private mount namespaces** with hidden bind mounts that hold block device references. These are invisible to standard process inspection tools.

**This decomposition applies to:**
- Reimaging or wiping disks on systems running systemd
- LVM migration on Ubuntu 20.04+ or any systemd-based system
- Any block device operation that returns "Device or resource busy" despite no visible holders

---

## Decomposition Steps

| Step | File | What It Does |
|------|------|-------------|
| 00 | `00-decomposition-plan.md` | This file — overview and navigation |
| 01 | `01-prompt-check-standard-tools.md` | Run `lsof`, `fuser`, `lslocks` to confirm no visible holders |
| 02 | `02-prompt-check-mountinfo.md` | Search `/proc/*/mountinfo` for private mount namespaces |
| 03 | `03-prompt-identify-services.md` | Map mount entries to systemd services and their `ProtectSystem` directives |
| 04 | `04-prompt-evaluate-live-unmount.md` | Attempt live unmount and assess systemd auto-restart risk |
| 05 | `05-prompt-pivot-to-early-boot.md` | Create one-shot early-boot systemd service for safe offline reconfiguration |
| 06 | `06-prompt-verify-post-reboot.md` | After reboot, verify LVM layout, data integrity, and mount points |

---

## Key Insight

> **Standard tools (`lsof`, `fuser`) do not see mount namespace holders.** Only `/proc/*/mountinfo` reveals the true state of mount namespace references.

When `wipefs` returns "Device or resource busy" and no process holds the device, the blocker is almost certainly a **mount namespace** created by systemd's `ProtectSystem` or `PrivateTmp` directives. These are used by:

- `systemd-resolved` (DNS resolution)
- `systemd-journald` (logging)
- `rsyslog` (alternative logging)
- `polkitd` (policy kit)
- `cron` (scheduled tasks)
- `dbus-daemon` (system bus)

All common on Ubuntu server/desktop installs.

---

## When to Use This Decomposition

| Symptom | Likely Cause |
|---------|-----------|
| `wipefs -a /dev/sdX` → "Device or resource busy" | Mount namespace or active swap |
| `pvcreate /dev/sdX` → "Can't open /dev/sdX exclusively" | Same — device held by kernel |
| `umount -l /mountpoint` succeeds but `partprobe` still fails | Lazy unmount detached filesystem but namespace still holds block device |
| `blockdev --rereadpt /dev/sdX` → "BLKRRPART: Device or resource busy" | Same |
| `lsof`, `fuser`, `lslocks` all show nothing | **Strong indicator: mount namespaces** |

---

## Alternative Approaches (Not Recommended)

| Approach | Why It Usually Fails |
|----------|---------------------|
| Kill processes one by one | systemd auto-restarts them immediately |
| Mask services without stopping all at once | Race condition — one service restart before others finish |
| Force with `dd if=/dev/zero` | Succeeds on raw device but partition table still cached by kernel namespaces |
| Reboot from live USB | Works but requires physical intervention and breaks automation |

**The early-boot service approach is the only reliable automated solution** when working remotely on a systemd-protected system.

---

## Prerequisites

- SSH access to target node with NOPASSWD sudo
- `/var` or other mount points on the target disk (triggered systemd services)
- Tools available: `lsof`, `fuser`, `awk`, `grep`, `sed`, `systemctl`
- Optional but recommended: existing `systemd` knowledge or access to service file locations

## Expected Resolution Time

| Phase | Time |
|-------|------|
| Diagnosis (steps 1-3) | 2-5 minutes |
| Decision: live vs. early-boot (step 4) | 1 minute |
| Early-boot service creation (step 5) | 5-10 minutes |
| Execution + reboot + verification (step 6) | 10-15 minutes |
| **Total** | **20-30 minutes** |

---

## Next Steps After Completion

After this decomposition resolves the device busy issue, the actual LVM work can proceed:
- `pvcreate /dev/sda /dev/sdb /dev/sdc`
- `vgcreate vg-lab ...`
- `lvcreate` and `mkfs.ext4`
- Data restoration from staging
- fstab update with UUIDs

See `ansible/playbooks/cleanup-lab-nodes.yml` for swap standardization logic that may apply.
