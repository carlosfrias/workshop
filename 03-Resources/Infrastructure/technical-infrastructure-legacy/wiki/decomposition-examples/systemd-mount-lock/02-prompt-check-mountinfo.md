# Step 02: Search /proc/*/mountinfo for Private Mount Namespaces

**Purpose:** Find the true holders of the block device by searching all process mount namespaces.

**Command:**
```bash
# Search all processes for mounts containing the target mountpoints
sudo grep -r -E "/var|/tmp|/srv|/usr/local|/opt|/var/log" /proc/*/mountinfo 2>/dev/null | head -20

# More focused: find which PIDs hold mounts backed by sda/sdb/sdc
for dev in sda sdb sdc; do
  major_minor=$(stat -c '%t:%T' /dev/$dev)
  echo "=== /dev/$dev ($major_minor) ==="
  sudo awk -v dev="$major_minor" '
    /\/ (var|tmp|srv|usr\/local|opt|var\/log) / {
      # Check if this mountinfo line references our device
      # We need to look at the mount source (3rd column in mountinfo)
      # and the device major:minor
    }
  ' /proc/*/mountinfo 2>/dev/null | head -5
done

# Simpler: just search for the mountpoint strings
sudo grep -l "sda\|sdb\|sdc" /proc/*/mountinfo 2>/dev/null | while read f; do
  pid=$(echo "$f" | sed 's/.*proc\/\(.*\)\/mountinfo/\1/')
  echo "=== PID $pid ==="
  cat /proc/$pid/cmdline | tr '\0' ' '
  echo ""
done | head -30
```

**Expected Output:**
```
/proc/1033/mountinfo:
1033 systemd-resolve
372 348 8:33 / /var ro,nosuid,relatime shared:182 - ext4 /dev/sdc1
/proc/1046/mountinfo:
1046 cron
...
```

**What to Look For:**
- Any PID that shows bind mounts (`8:33` → device major:minor for `/dev/sdc1`)
- Mount options including `ro` (read-only bind) from `ProtectSystem`
- Services you didn't start but which show mount entries

**Decision:**
- If **mount namespaces found** → proceed to Step 03 (identify services)
- If **nothing found** → check for loop devices (`losetup -a`) or device-mapper (`dmsetup ls`)
