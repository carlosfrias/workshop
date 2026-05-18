# Creating an Ubuntu 24.04 Autoinstall USB for Lab Node Reimaging

**Version:** 1.0  
**Scope:** Reimage any Trading Desk lab node to Ubuntu 24.04.4 LTS with zero manual interaction  
**Target:** Orchestrator (macOS Apple M1 Pro)  
**Tools:** `brew`, `curl`, `xorriso`, `dd`, `bsdtar`, `ssh`, `scp`

---

## Prerequisites on the Orchestrator

Install the tools needed to modify and flash the ISO. These are **not** standard macOS utilities.

```bash
# 1. Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. xorriso — the ISO manipulation tool
brew install xorriso

# 3. Verify
which xorriso    # should print /usr/local/bin/xorriso (or /opt/homebrew/bin/xorriso)
which bsdtar     # usually pre-installed on macOS via libarchive
which dd         # pre-installed
which ssh        # pre-installed
```

---

## Step-by-Step Process

### STEP 1: Download the Ubuntu Server ISO

Download **Ubuntu 24.04.4 LTS Server** (not Desktop) amd64 image.

```bash
mkdir -p ~/Downloads/binaries

curl -L -o ~/Downloads/binaries/ubuntu-24.04.4-live-server-amd64.iso \
  "https://releases.ubuntu.com/24.04/ubuntu-24.04.4-live-server-amd64.iso"

# Verify download
ls -lh ~/Downloads/binaries/ubuntu-24.04.4-live-server-amd64.iso
# Expected: ~3.2GB
```

**Why Server ISO?** Desktop ISOs include gdm, GNOME, and snaps that cause hangs on headless hardware. Server ISOs are smaller and boot cleanly to autoinstall.

---

### STEP 2: Create the Autoinstall YAML (`user-data`)

`user-data` follows the **cloud-init autoinstall schema** used by Subiquity (Ubuntu's installer).

**Critical sections:** identity, ssh, storage, packages, late-commands.

**Two ways to handle the password:**

**Option A: Prompt the user (recommended)**
```bash
read -s -p "Password for 'friasc' on new nodes: " PLAINTEXT_PASS
echo
HASHED_PASS=$(openssl passwd -6 "$PLAINTEXT_PASS")
```

**Option B: Generate and record a random password**
```bash
PLAINTEXT_PASS=$(openssl rand -base64 24)
HASHED_PASS=$(openssl passwd -6 "$PLAINTEXT_PASS")
echo "Password for 'friasc': $PLAINTEXT_PASS"
# Copy the plaintext somewhere safe
```

**Then create the YAML:**

```bash
cat > /tmp/user-data << 'EOF'
#cloud-config
# Ubuntu 24.04.4 LTS Server Autoinstall
# Target: Lab node with NVMe SSD + optional second HDD
autoinstall:
  version: 1
  locale: en_US.UTF-8
  keyboard:
    layout: us

  identity:
    hostname: fnetX    # Change per node
    username: friasc
    password: "HASH_GOES_HERE"   # Insert $HASHED_PASS from openssl

  ssh:
    install-server: true
    authorized-keys:
      - ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDGp8QOwHzmaAATAU2xxPfp8qhJvjloUFmY10Motg4SpwaNU2YbCqpn9y6IElTbvUJLXM/zQxRQ8MHEya98rimYCeAJHCMyA1+O/ib+49WNxXI+Rz1DKb5GCQDeTuhdJ/nY3jUYx9AZvMLcpo6cASH0GH27bFh+DjZPDw/Qh9oqt0Zb00/PqjMFNztZYA1Eg3v6pYfYtFR2uJRI9Eh29bKJb7QSruTzc7OkBY6B7IHQciYli7QMtgzIRrNsFSHpwd7lUKt20TLirVTo6EEU0Atds1AE0y2SyisiW4ZMDJKcBr3n1JwyzlIfWg6WBB+r3g5xUY9cwPklnq7opG3+rj/LzyHI3UU60XJETpBYVZIkGHjvtS7T6x8NXyniniW0HRgB5DmrnM8sSGV5PGsve2ga48PXnJgzkrtaUIXmHnWjgAZRzkj73pMJGJ6DaHxmAcZv05QU0xufVIPetUrytLhZE4HcEAL2TR5WZer/+49ot6yrBSBEWPBtUpQE5d9+Tv8= friasc@Carloss-MacBook-Pro.local
    allow-pw: true

  # Storage: use Subiquity's layout shorthand, NOT explicit device paths.
  # This selects the largest SSD automatically and creates EFI+/boot+/root LVM.
  storage:
    layout:
      name: lvm
      match:
        size: largest
        ssd: true

  packages:
    - openssh-server
    - vim
    - curl
    - htop
    - net-tools
    - docker.io
    - wireguard
    - wireguard-tools
    - nfs-common
    - lvm2

  late-commands:
    - curtin in-target --target=/target -- usermod -aG docker friasc
    - curtin in-target --target=/target -- systemctl enable docker || true
    # CRITICAL: prevent gdm from hanging on headless desktop NUCs
    - curtin in-target --target=/target -- systemctl set-default multi-user.target || true
EOF

# Now replace the placeholder with the real hash
sed -i '' 's|HASH_GOES_HERE|'$HASHED_PASS'|' /tmp/user-data
```

### `meta-data` (minimal, required by cloud-init)

```bash
cat > /tmp/meta-data << 'EOF'
instance-id: fnetX-reimage-2026-04-30
local-hostname: fnetX
EOF
```

---

### STEP 3: Modify the ISO's `grub.cfg`

**Why this is needed:** We must add the autoinstall boot parameter to the ISO's GRUB menu entry so the node boots straight into unattended install.

**Critical syntax:**
- `ds=nocloud-net;s=http://...` tells cloud-init to fetch config from HTTP, not from a cloud provider.
- In grub, `;` is a **statement separator** (like bash). The `s=http://` part after the semicolon is **silently dropped** unless wrapped in **double quotes**.
- `cloud-config-url=/dev/null` prevents the installer from hanging while searching for a cloud metadata service.

**Extract the original grub.cfg:**

```bash
cd /tmp
rm -rf /tmp/original-grub
bsdtar xf ~/Downloads/binaries/ubuntu-24.04.4-live-server-amd64.iso boot/grub/grub.cfg
```

**Create the replacement `grub.cfg`:**

```bash
cat > /tmp/modified-grub.cfg << 'GRUBEOF'
set timeout=5

loadfont unicode

set menu_color_normal=white/black
set menu_color_highlight=black/light-gray

menuentry "Try or Install Ubuntu Server" {
	set gfxpayload=keep
	linux	/casper/vmlinuz autoinstall "ds=nocloud-net;s=http://192.168.0.141:8081/" cloud-config-url=/dev/null ---
	initrd	/casper/initrd
}
menuentry "Ubuntu Server with the HWE kernel" {
	set gfxpayload=keep
	linux	/casper/hwe-vmlinuz autoinstall "ds=nocloud-net;s=http://192.168.0.141:8081/" cloud-config-url=/dev/null ---
	initrd	/casper/hwe-initrd
}
grub_platform
if [ "$grub_platform" = "efi" ]; then
menuentry 'Boot from next volume' {
	exit 1
}
menuentry 'UEFI Firmware Settings' {
	fwsetup
}
else
menuentry 'Test memory' {
	linux16 /boot/memtest86+x64.bin
}
fi
GRUBEOF
```

**Note:** The double quotes around `"ds=nocloud-net;s=http://192.168.0.141:8081/"` are **mandatory**. Without them, the `s=...` part is discarded by GRUB.

---

### STEP 4: Rebuild the ISO with `xorriso`

```bash
xorriso -indev ~/Downloads/binaries/ubuntu-24.04.4-live-server-amd64.iso \
  -outdev /tmp/ubuntu-24.04.4-autoinstall-fixed.iso \
  -boot_image any replay \
  -pathspecs on \
  -overwrite on \
  -add "/boot/grub/grub.cfg=/tmp/modified-grub.cfg"
```

**Output:** `/tmp/ubuntu-24.04.4-autoinstall-fixed.iso` (~3.2GB)

**Verify the new ISO contains the modified grub.cfg:**

```bash
cd /tmp
rm -rf /tmp/verify-grub
bsdtar xf /tmp/ubuntu-24.04.4-autoinstall-fixed.iso boot/grub/grub.cfg
grep 'ds=nocloud-net' /tmp/verify-grub/boot/grub/grub.cfg
# Should show the quoted URL string
```

---

### STEP 5: Write the ISO to USB with `dd`**

**⚠️ WARNING:** `/dev/rdisk4` is an example. Verify your actual USB device with `diskutil list` first. Writing to the wrong disk will destroy data.

```bash
# 1. Identify the USB device
diskutil list | grep -E "external|USB|disk4"

# 2. Unmount the USB before writing
diskutil unmountDisk force disk4

# 3. Write ISO to USB (takes ~3-5 minutes)
sudo dd if=/tmp/ubuntu-24.04.4-autoinstall-fixed.iso of=/dev/rdisk4 bs=1m

# 4. Eject cleanly
diskutil eject disk4
```

**After `dd`:** The USB is bootable. Plug it into any lab node, select USB from the boot menu, and the autoinstall runs without manual interaction.

---

### STEP 6: Serve `user-data` and `meta-data` via HTTP

The autoinstall USB points to `http://192.168.0.141:8081/user-data`. Any node on the LAN can serve this — in the lab setup, fnet1 is the HTTP server.

```bash
# On the node serving HTTP (e.g., fnet1)
mkdir -p /tmp/autoinstall-server
cp /tmp/user-data /tmp/meta-data /tmp/autoinstall-server/
cd /tmp/autoinstall-server && python3 -m http.server 8081
```

Verify the node can reach it:
```bash
curl -s http://192.168.0.141:8081/user-data | head -5
```

---

## What the Corrected Parameters Do

| Parameter | Purpose | Evidence |
|-----------|---------|----------|
| `autoinstall` | Triggers unattended mode in Subiquity | Ubuntu Server documentation |
| `ds=nocloud-net` | Tells cloud-init to use HTTP instead of AWS/Azure metadata | cloud-init docs |
| `"ds=...;s=..."` | **Quoted** because `;` is GRUB's statement separator | AskUbuntu accepted answer, verified 2026-04-30 |
| `cloud-config-url=/dev/null` | Prevents installer from hanging waiting for a cloud metadata service | Community testing |
| `---` | GRUB keyword separating kernel params from initrd params (standard convention) | GRUB manual |

---

## Common Failures and Evidence-Based Fixes

| Failure | Root Cause | Fix |
|---------|-----------|-----|
| Blue language screen installer | GRUB dropped `s=http://` due to unquoted `;` | Wrap `ds=` in double quotes |
| "An error occurred" after boot | Initramfs lacks modules for new kernel's LVM | Boot older kernel in GRUB → `update-initramfs -c -k all` |
| Black screen, no SSH after install | `graphical.target` default → gdm waits for nonexistent monitor | Add `systemctl set-default multi-user.target` to late-commands |
| Installer crashes immediately | Explicit multi-disk LVM config in user-data | Use `storage: {layout: {name: lvm, match: ...}}` |
| Node can't reach HTTP server | Firewall, wrong IP, or server not started | `curl http://192.168.0.141:8081/user-data` from node |

---

## Files Reference

| File | Location | Purpose |
|------|----------|---------|
| Source ISO | `~/Downloads/binaries/ubuntu-24.04.4-live-server-amd64.iso` | Canonical Ubuntu Server 24.04.4 |
| Modified ISO | `/tmp/ubuntu-24.04.4-autoinstall-fixed.iso` | Hardcoded autoinstall (quoted `ds=`) |
| `user-data` | `/tmp/user-data` | Cloud-init autoinstall YAML |
| `meta-data` | `/tmp/meta-data` | Cloud-init metadata |
| `grub.cfg` | `/tmp/modified-grub.cfg` | Modified bootloader config |

---

## Routing Notes
- `infrastructure` (local qwen3:8b): For status checks, SSH commands, live verification
- `reasoning` (cloud): For analysis and planning
- `structured` (local gemma4:e4b): For log parsing, file operations
- Domain: `technical-infrastructure`

---

**End of prompt.**
