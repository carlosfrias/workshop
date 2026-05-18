# Step 06: Verify LVM Layout, Data Integrity, and Mount Points

**Purpose:** After the early-boot service runs and the system reboots, confirm everything is correct.

**Verification Commands:**

```bash
# 1. Check disk layout
lsblk -o NAME,SIZE,TYPE,MOUNTPOINTS

# 2. Check LVM
sudo pvs
sudo vgs
sudo lvs

# 3. Check mounts
df -h | grep -E "(vg-lab|lv-)"

# 4. Verify fstab has UUIDs (not old partition references)
grep -E "(UUID|vg-lab)" /etc/fstab

# 5. Verify service disabled itself
systemctl is-enabled fnet1-lvm-setup.service 2>&1
# Expected: "disabled" (service ran once and self-disabled)

# 6. Check service log from initial boot
journalctl -u fnet1-lvm-setup --no-pager | head -50

# 7. Data integrity — compare sizes
for dir in /var /srv /usr/local /opt /var/log /tmp; do
  echo "$dir: $(du -sh $dir | cut -f1)"
done
```

**Expected Output:**
```
NAME                SIZE TYPE MOUNTPOINTS
sda               931.5G disk 
sdb               931.5G disk 
sdc               931.5G disk 
sr0                1024M rom  
nvme0n1           232.9G disk 
├─nvme0n1p1         954M part /boot
├─nvme0n1p2           1G part /boot/efi
└─nvme0n1p3       230.9G part /
  └─vg-lab-lv-var    50G lvm  /var
  └─vg-lab-lv-srv   200G lvm  /srv
  └─...etc
```

**Acceptance Criteria:**
- [ ] `lsblk` shows no sda1/sda2/sda3 partitions (only whole disks)
- [ ] `pvs` shows /dev/sda, /dev/sdb, /dev/sdc as physical volumes
- [ ] `vgs` shows `vg-lab` with ~2.8TB total
- [ ] `lvs` shows 7 logical volumes (var, srv, varlog, tmp, opt, usrlocal, archive)
- [ ] `df -h` shows all mountpoints with expected sizes
- [ ] `grep sda /etc/fstab` returns nothing (old partitions gone)
- [ ] `grep UUID /etc/fstab` shows 7 entries for vg-lab volumes
- [ ] Data sizes match pre-rebuild staging sizes
- [ ] Service is disabled (won't run again on next boot)

**If Something Is Wrong:**
- Check `journalctl -u fnet1-lvm-setup` for errors
- Mount the old NVMe partition from a live USB if recovery is needed
- The staging data on NVMe (`/mnt/staging`) should still be intact if the service didn't reach step 8

**Cleanup After Verification:**
```bash
# Remove staging data (free up NVMe space)
sudo rm -rf /mnt/staging

# Remove service file (optional — it's already disabled)
sudo rm /etc/systemd/system/fnet1-lvm-setup.service
sudo systemctl daemon-reload
```

---

## When This Decomposition Was Used

**Session:** 2026-05-01, fnet1 LVM rebuild  
**Agent:** `fd02c010-b47d-4eb`  
**Outcome:** Agent discovered systemd mount namespaces, pivoted from live unmounting to early-boot service approach. Service was created and verified as viable. All tools (`pvcreate`, `vgcreate`, `lvcreate`) confirmed available.
