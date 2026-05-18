# Step 01: Run Standard Tools to Confirm No Visible Holders

**Purpose:** Exhaust standard diagnostic tools so we can conclusively rule out visible process/file holders and know we're dealing with mount namespaces.

**Command:**
```bash
# Check for open files on the block device
sudo lsof /dev/sda /dev/sdb /dev/sdc 2>/dev/null

# Check for processes using the device
sudo fuser -v /dev/sda /dev/sdb /dev/sdc 2>/dev/null

# Check for active file locks
sudo lslocks | grep -E "(sda|sdb|sdc)"

# Check swapon status
swapon --show | grep -E "(sda|sdb|sdc)"
```

**Expected Output if Mount Namespaces:**
- `lsof`: nothing
- `fuser`: nothing
- `lslocks`: nothing
- `swapon`: nothing (swap already turned off)

**Expected Output if Normal Process Holder:**
- `lsof` or `fuser` shows a process name and PID

**Decision:**
- If **anything shows a process** → kill that process and retry
- If **all tools return nothing** → proceed to Step 02 (mountinfo search)

**Key Learning:** Never conclude "device is free" based solely on `lsof` and `fuser`.
