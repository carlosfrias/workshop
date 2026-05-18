#!/bin/bash
# fnet1-lvm-setup.sh
# Early-boot LVM setup script for systemd-protected systems
# Run from a systemd service after local-fs.target, before sysinit.target
# See: wiki/decomposition-examples/systemd-mount-lock/00-decomposition-plan.md

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

# Step 7: Mount new volumes
mkdir -p /var /srv /var/log /tmp /opt /usr/local /srv/archive
mount /dev/vg-lab/lv-var /var
mount /dev/vg-lab/lv-srv /srv
mount /dev/vg-lab/lv-varlog /var/log
mount /dev/vg-lab/lv-tmp /tmp
mount /dev/vg-lab/lv-opt /opt
mount /dev/vg-lab/lv-usrlocal /usr/local
mount /dev/vg-lab/lv-archive /srv/archive

# Step 8: Restore data from staging
if [ -d /mnt/staging ]; then
  echo "=== Restoring data from staging ==="
  cp -a /mnt/staging/var/* /var/ 2>/dev/null || true
  cp -a /mnt/staging/srv/* /srv/ 2>/dev/null || true
  cp -a /mnt/staging/usr-local/* /usr/local/ 2>/dev/null || true
  cp -a /mnt/staging/opt/* /opt/ 2>/dev/null || true
  cp -a /mnt/staging/varlog/* /var/log/ 2>/dev/null || true
  cp -a /mnt/staging/tmp/* /tmp/ 2>/dev/null || true
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
