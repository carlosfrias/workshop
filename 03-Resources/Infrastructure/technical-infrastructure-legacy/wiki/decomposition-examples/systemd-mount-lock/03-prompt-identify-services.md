# Step 03: Map Mount Namespaces to Systemd Services

**Purpose:** Convert PIDs from mountinfo into systemd service names so we know what to stop.

**Command:**
```bash
# For each PID found in Step 02, get its service name
for pid in 1033 1046; do  # Replace with actual PIDs from Step 02
  echo "=== PID $pid ==="
  ps -p $pid -o pid,comm,cgroup --no-headers 2>/dev/null
  sudo systemctl status $pid 2>/dev/null | head -3
  # Try to get the exact service unit
  sudo systemctl status --full $pid 2>/dev/null | grep -oE "[^ ]+\.service" | head -1
done

# Alternative: check service files for ProtectSystem/PrivateTmp
grep -r "ProtectSystem\|PrivateTmp" /etc/systemd/system/*.service /usr/lib/systemd/system/*.service 2>/dev/null | head -20
```

**Expected Service Names (Ubuntu 24.04):**
```
systemd-resolved.service (ProtectSystem=yes, ProtectHome=yes)
systemd-journald.service (ProtectSystem=strict, ProtectHome=yes)
rsyslog.service (ProtectSystem=restricted, PrivateTmp=yes)
polkitd.service (ProtectSystem=strict, PrivateTmp=yes)
cron.service (ProtectSystem=strict, PrivateTmp=yes)
dbus-daemon.service (ProtectSystem=strict, PrivateTmp=yes)
```

**Key Insight:**
The `ProtectSystem` directive creates a read-only bind mount of the root filesystem into the service's mount namespace. The service then gets a view where certain directories are read-only or hidden. This bind mount — even though it's read-only — holds a reference to the underlying block device.

**Decision:**
- If **systemd services identified** → proceed to Step 04 (evaluate live unmount vs. early-boot)
