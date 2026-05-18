# Step 04: Evaluate Live Unmount vs. Early-Boot Service

**Purpose:** Attempt to stop services and unmount in a live session. If systemd auto-restart defeats us, pivot to the reliable approach.

**Command (Live Attempt):**
```bash
# Stop services that hold mount namespaces
sudo systemctl stop systemd-resolved systemd-journald rsyslog cron polkitd dbus-daemon 2>/dev/null

# Lazy unmount the filesystems (detaches from mount tree, not block device)
sudo umount -l /var /var/log /tmp /usr/local /opt /srv 2>/dev/null

# Check if block devices are still held
sudo lsblk -o NAME,SIZE,TYPE,MOUNTPOINTS | grep -E "(sda|sdb|sdc)"

# Try wipefs again
sudo wipefs -a /dev/sda /dev/sdb /dev/sdc 2>&1 | head -5
```

**Expected Failure (Mount Namespaces):**
```
wipefs: error: /dev/sda: probing initialization failed: Device or resource busy
```

**Why It Fails:**
Even after stopping services and lazy unmounting, the kernel may still hold references because:
- systemd auto-restarted some services (journald, polkitd) before we could wipe
- Other services have `Restart=always` directives
- The mount namespace references persist in kernel structures even after process exit

**The Pivot — Decision Time:**

| Condition | Action |
|-----------|--------|
| `wipefs` works after stopping services | Live approach succeeded — proceed with LVM |
| `wipefs` still fails | **Pivot to early-boot service** (Step 05) |
| Services auto-restart immediately | **Pivot to early-boot service** (Step 05) |
| Session drops during service stops (SSH depends on systemd socket) | **Pivot to early-boot service** (Step 05) |

**Key Warning:**
Stopping `systemd-journald` or `systemd-logind` may drop your SSH session. If this happens, the only recovery is:
- Physical console access, OR
- Reboot and use the early-boot service approach anyway

**Recommendation:** If any service auto-restarts, skip further live attempts and go directly to Step 05. The time spent fighting auto-restart is better invested in the reliable early-boot approach.
