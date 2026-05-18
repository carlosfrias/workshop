# Step 05: Create One-Shot Early-Boot Systemd Service

**Purpose:** Create a systemd service that runs after rootfs is mounted but before any `ProtectSystem` services start. This is the clean, reliable way to reconfigure storage on a systemd system.

**How It Works:**
1. Service starts after `local-fs.target` (all filesystems from `/etc/fstab` are mounted)
2. Service runs before `sysinit.target` (before services with `ProtectSystem`/`PrivateTmp` start)
3. Service executes the full LVM creation + data restore + fstab update
4. Service is `Type=oneshot` — runs once and exits
5. RemainAfterExit=yes — systemd considers the target reached

**Files to Create:**

1. **Systemd service:** `/etc/systemd/system/fnet1-lvm-setup.service`
2. **Setup script:** `/usr/local/bin/fnet1-lvm-setup.sh` — copy from `scripts/fnet1-lvm-setup.sh` in this decomposition. It handles: stop services → wipe → pvcreate → vgcreate → lvcreate → mkfs → mount → restore data → update fstab → self-disable.

**The script is also embedded below for immediate reading:**

```ini
[Unit]
Description=fnet1 LVM setup from early boot
After=local-fs.target
Before=sysinit.target
DefaultDependencies=no
RequiresMountsFor=/ /mnt/staging

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/local/bin/fnet1-lvm-setup.sh
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=sysinit.target
```

**Setup script (`/usr/local/bin/fnet1-lvm-setup.sh`):**

```bash
#!/bin/bash
# fnet1-lvm-setup.sh
# Early-boot LVM setup script for systemd-protected systems
# Run from a systemd service after local-fs.target, before sysinit.target

set -e

exec > >(journalctl -t fnet1-lvm-setup)
exec 2>&1

echo "=== fnet1 LVM Setup Starting ==="
lsblk -o NAME,SIZE,TYPE,MOUNTPOINTS

# Step 1: Unmount old partitions (should already be unmounted at this stage)
umount -l /var /var/log /tmp /usr/local /opt /srv 2>/dev/null || true

# Step 2: Wipe disks
wipefs -a /dev/sda /dev/sdb /dev/sdc || true
dd if=/dev/zero of=/dev/sda bs=1M count=10 status=none || true
dd if=/dev/zero of=/dev/sdb bs=1M count=10 status=none || true
dd if=/dev/zero of=/dev/sdc bs=1M count=10 status=none || true

# Step 3: Create physical volumes
pvcreate /dev/sda /dev/sdb /dev/sdc

# Step 4: Create volume group
vgcreate vg-lab /dev/sda /dev/sdb /dev/sdc

# Step 5: Create logical volumes
lvcreate -n lv-var -L 50G vg-lab
lvcreate -n lv-srv -L 200G vg-lab
lvcreate -n lv-varlog -L 20G vg-lab
lvcreate -n lv-tmp -L 20G vg-lab
lvcreate -n lv-opt -L 20G vg-lab
lvcreate -n lv-usrlocal -L 20G vg-lab
lvcreate -n lv-archive -l 100%FREE vg-lab

# Step 6: Format
for lv in var srv varlog tmp opt usrlocal archive; do
  mkfs.ext4 -L "lv-$lv" /dev/vg-lab/lv-$lv
done

# Step 7: Mount new volumes — parent dirs first, then children
# Mount /var FIRST
mkdir -p /var
mount /dev/vg-lab/lv-var /var
# Now create child dirs inside mounted /var
mkdir -p /var/log
# Mount /var/log
mount /dev/vg-lab/lv-varlog /var/log

# Mount /srv
mkdir -p /srv
mount /dev/vg-lab/lv-srv /srv
# Create child dir inside mounted /srv
mkdir -p /srv/archive
# Mount /srv/archive
mount /dev/vg-lab/lv-archive /srv/archive

# Mount remaining (no children)
mkdir -p /tmp
mount /dev/vg-lab/lv-tmp /tmp
mkdir -p /opt
mount /dev/vg-lab/lv-opt /opt
mkdir -p /usr/local
mount /dev/vg-lab/lv-usrlocal /usr/local

# Step 8: Restore data from staging using rsync (handles symlinks correctly)
if [ -d /mnt/staging ]; then
  echo "=== Restoring data from staging ==="
  for dir in var srv usr-local opt varlog tmp; do
    target=""
    case $dir in
      var) target="/var" ;;
      srv) target="/srv" ;;
      usr-local) target="/usr/local" ;;
      opt) target="/opt" ;;
      varlog) target="/var/log" ;;
      tmp) target="/tmp" ;;
    esac
    if [ -d "/mnt/staging/$dir" ] && [ -n "$target" ]; then
      echo "Restoring $dir to $target..."
      rsync -a --exclude='lost+found' --exclude='.Trash*' "/mnt/staging/$dir/" "$target/" || true
    fi
  done
  echo "=== Data restore complete ==="
fi

# Step 9: Update fstab
sed -i '/sda/d; /sdb/d; /sdc/d' /etc/fstab
for lv in var srv varlog tmp opt usrlocal archive; do
  uuid=$(blkid -s UUID -o value /dev/vg-lab/lv-$lv)
  mountpoint=$(case $lv in var) echo /var;; srv) echo /srv;; varlog) echo /var/log;; tmp) echo /tmp;; opt) echo /opt;; usrlocal) echo /usr/local;; archive) echo /srv/archive;; esac)
  echo "UUID=$uuid $mountpoint ext4 defaults 0 2" >> /etc/fstab
done

# Step 10: Disable this service so it doesn't run again
systemctl disable fnet1-lvm-setup.service

echo "=== fnet1 LVM Setup Complete ==="
echo "Rebooting in 5 seconds..."
sleep 5
```

**Enable and Prepare:**
```bash
sudo cp /path/to/decomposition/scripts/fnet1-lvm-setup.sh /usr/local/bin/fnet1-lvm-setup.sh
sudo chmod +x /usr/local/bin/fnet1-lvm-setup.sh
sudo systemctl daemon-reload
sudo systemctl enable fnet1-lvm-setup.service
```

**Important:** Do NOT start the service now (it would fail — old mounts are still active). Only enable it. It runs on next boot.

**Staging Data Prerequisite:**
Before rebooting, ensure staging data is on NVMe:
```bash
sudo mkdir -p /mnt/staging/{var,srv,usr-local,opt,varlog,tmp}
sudo cp -a /var/* /mnt/staging/var/    # Do this BEFORE enabling the service
sudo cp -a /srv/* /mnt/staging/srv/
# etc.
```

**Decision:** After enabling the service, reboot. Proceed to Step 06 for verification.
