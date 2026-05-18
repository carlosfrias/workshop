# Ubuntu 24.04 Autoinstall for Trading Desk Lab Nodes
**Version:** 1.1 (2026-04-30) — includes Recovery Mode password reset  
**Domain:** `technical-infrastructure`  
**Status:** ✅ Verified on fnet2; ready for fnet3–fnet7

---

## What This Prompt Covers

Standardized, zero-interaction Ubuntu 24.04 LTS reinstallation for all Trading Desk lab nodes (fnet2–fnet7), including an emergency password reset procedure for when the placeholder password is unknown.

---

## Part 1: Autoinstall ISO Creation

### Prerequisites on Orchestrator (macOS)
- `brew install xorriso` — ISO manipulation tool
- `~/Downloads/binaries/ubuntu-24.04.4-live-server-amd64.iso` — source ISO
- `ssh-keygen` key at `~/.ssh/id_rsa.pub` (pre-authorized on all lab nodes)

### Step 1.1: Correct grub.cfg

**CRITICAL:** The `ds=` parameter must be enclosed in **double quotes** inside grub. GRUB interprets semicolons as statement separators.

**WRONG** (causes interactive installer / language screen):
```grub
linux /casper/vmlinuz autoinstall ds=nocloud-net\;s=http://192.168.0.141:8081/ ---
```

**CORRECT** (evidence: AskUbuntu accepted answer, verified 2026-04-30):
```grub
linux /casper/vmlinuz autoinstall "ds=nocloud-net;s=http://192.168.0.141:8081/" cloud-config-url=/dev/null ---
```

### Step 1.2: Create grub.cfg File

```grub
set timeout=5

loadfont unicode

set menu_color_normal=white/black
set menu_color_highlight=black/light-gray

menuentry "Try or Install Ubuntu Server" {
    set gfxpayload=keep
    linux	/casper/vmlinuz autoinstall "ds=nocloud-net;s=http://192.168.0.141:8081/" cloud-config-url=/dev/null ---
    initrd	/casper/initrd
}
```

### Step 1.3: Rebuild ISO with xorriso

```bash
xorriso -indev ~/Downloads/binaries/ubuntu-24.04.4-live-server-amd64.iso \
  -outdev /tmp/ubuntu-24.04.4-autoinstall-fixed.iso \
  -boot_image any replay \
  -pathspecs on \
  -overwrite on \
  -add "/boot/grub/grub.cfg=/path/to/corrected-grub.cfg"
```

### Step 1.4: Write to USB (macOS)

```bash
diskutil unmountDisk force disk4
sudo dd if=/tmp/ubuntu-24.04.4-autoinstall-fixed.iso of=/dev/rdisk4 bs=1m
diskutil eject disk4
```

---

## Part 2: Autoinstall HTTP Config (user-data)

### Storage: Use Layout Shorthand — NOT Explicit Disk Paths

**WRONG** (crashes Subiquity when multi-disk explicit paths are used):
```yaml
storage:
  config:
    - { ptable: gpt, path: /dev/nvme0n1, wipe: superblock-recursive, ... }
    - { device: disk-nvme, ... }
```

**CORRECT** (evidence: Subiquity's native layout handler, verified 2026-04-30):
```yaml
storage:
  layout:
    name: lvm
    match:
      size: largest
      ssd: true
```

This reliably selects the largest SSD (nvme0n1), creates EFI + /boot + LVM automatically. The second disk (sda) must be configured post-OS.

### Minimal Working user-data

```yaml
#cloud-config
# Ubuntu 24.04.4 LTS Server Autoinstall for Trading Desk lab nodes
autoinstall:
  version: 1
  locale: en_US.UTF-8
  keyboard:
    layout: us
  identity:
    hostname: fnetX         # Change per node: fnet2, fnet3, etc.
    username: friasc
    password: "$PLACEHOLDER_HASH$"  # See Part 2A: Password Handling
  ssh:
    install-server: true
    authorized-keys:
      - ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDGp8QOwHzmaAATAU2xxPfp8qhJvjloUFmY10Motg4SpwaNU2YbCqpn9y6IElTbvUJLXM/zQxRQ8MHEya98rimYCeAJHCMyA1+O/ib+49WNxXI+Rz1DKb5GCQDeTuhdJ/nY3jUYx9AZvMLcpo6cASH0GH27bFh+DjZPDw/Qh9oqt0Zb00/PqjMFNztZYA1Eg3v6pYfYtFR2uJRI9Eh29bKJb7QSruTzc7OkBY6B7IHQciYli7QMtgzIRrNsFSHpwd7lUKt20TLirVTo6EEU0Atds1AE0y2SyisiW4ZMDJKcBr3n1JwyzlIfWg6WBB+r3g5xUY9cwPklnq7opG3+rj/LzyHI3UU60XJETpBYVZIkGHjvtS7T6x8NXyniniW0HRgB5DmrnM8sSGV5PGsve2ga48PXnJgzkrtaUIXmHnWjgAZRzkj73pMJGJ6DaHxmAcZv05QU0xufVIPetUrytLhZE4HcEAL2TR5WZer/+49ot6yrBSBEWPBtUpQE5d9+Tv8= friasc@Carloss-MacBook-Pro.local
    allow-pw: true
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
```

### meta-data

```yaml
instance-id: fnetX-reimage-2026-04-30
local-hostname: fnetX
```

---

## Part 2A: Password Handling — CRITICAL

**Never use an unknown or placeholder password hash in the autoinstall config.** If the user cannot log in after install, recovery mode is required.

### Two Valid Approaches

#### Option A: Generate and Communicate (Recommended)

Before creating `user-data`, generate a strong random password, hash it, and **communicate the plaintext to the user**:

```bash
# Generate
PLAINTEXT_PASS=$(openssl rand -base64 24)
HASHED_PASS=$(openssl passwd -6 "$PLAINTEXT_PASS")

# Communicate to user immediately
echo "The autoinstall password for user 'friasc' is: $PLAINTEXT_PASS"
echo "Hash for user-data: $HASHED_PASS"

# Store securely
echo "$PLAINTEXT_PASS" | pbcopy  # macOS
echo "$PLAINTEXT_PASS" > ~/.autoinstall-password.txt
chmod 600 ~/.autoinstall-password.txt
```

**Then embed the hash:**
```yaml
identity:
  username: friasc
  password: "$HASHED_PASS"
```

#### Option B: Prompt the User

Ask the user for their desired password, hash it on the fly, and embed:

```bash
# Terminal prompt (user types plaintext, not echoed)
read -s -p "Password for 'friasc' on new nodes: " PLAINTEXT_PASS
echo
HASHED_PASS=$(openssl passwd -6 "$PLAINTEXT_PASS")

# Insert into user-data via sed
cat user-data-template.yaml | sed "s|PLAINTHOLDER|$HASHED_PASS|" > user-data.yaml
```

### What NOT to Do

**WRONG** (caused recovery mode on fnet2):
```yaml
# Never embed a pre-generated hash without recording the plaintext
password: "$6$rounds=4096$..."  # Unknown plaintext
```

**Why it's wrong:** Neither the user nor the operator can log in. SSH key auth may work, but `sudo` and password-based recovery (e.g., console access, Single User Mode) are impossible without recovery mode.

### Post-Install Password Change

After SSH key login is confirmed working, the user can change their password:
```bash
ssh friasc@fnetX
passwd
# Type new password twice
```

**Or the user can set it themselves immediately after login.**

---

## Part 3: HTTP Server on fnet1

```bash
mkdir -p /tmp/autoinstall-server
cp user-data meta-data /tmp/autoinstall-server/
cd /tmp/autoinstall-server && nohup python3 -m http.server 8081 > /tmp/http-server.log 2>&1 &
```

Verify: `curl -s http://192.168.0.141:8081/user-data | head -5`

---

## Part 4: Lab Node Status

| Node | IP | RAM | Current OS | Target OS | Method | Status |
|------|-----|-----|-----------|-----------|--------|--------|
| fnet1 | .141 | 15GB | Ubuntu 24.04 | N/A | Control plane | ✅ PXE + HTTP online |
| **fnet2** | **.142** | **14GB** | ~~Ubuntu 26.04 alpha~~ | **Ubuntu 24.04** | **USB autoinstall** | **✅ DONE** |
| fnet3 | .143 | 31GB | Ubuntu 20.04 EOL | Ubuntu 24.04 | PXE or USB | ⏳ Queued |
| fnet4 | .144 | 31GB | Ubuntu 20.04 EOL | Ubuntu 24.04 | PXE or USB | ⏳ Queued |
| fnet5 | .145 | 31GB | Ubuntu 20.04 EOL | Ubuntu 24.04 | PXE or USB | ⏳ Queued |
| fnet6 | .146 | 31GB | Ubuntu 22.04 | Ubuntu 24.04 | PXE or USB | ⏳ Queued |
| fnet7 | .147 | 15GB | Ubuntu 22.04 | Ubuntu 24.04 | PXE or USB | ⏳ Queued |

---

## Part 5: Recovery Mode Password Reset — Evidence-Based

**When:** Autoinstall succeeds but `friasc` password is unknown because a placeholder hash was used instead of communicating the plaintext. **Preventable by following Part 2A above.**  
**Source:** https://wiki.ubuntu.com/RecoveryMode, https://help.ubuntu.com/community/LostPassword  
**Duration:** ~2 minutes  
**Risk:** Zero — no data loss, no reinstall needed.

### Step 5.1: Reboot into GRUB Menu

1. **Power button** or `sudo reboot` (if SSH key is working)
2. As system reboots, **hold Shift** (BIOS systems) or **press Escape** repeatedly (UEFI systems)
3. The **GNU GRUB menu** appears (black screen, white text)

### Step 5.2: Select Recovery Mode

```
* Ubuntu
  Advanced options for Ubuntu                    ← SELECT THIS, press Enter
  UEFI Firmware Settings
```

Then on the submenu:

```
* Ubuntu, with Linux 6.8.0-52-generic
  Ubuntu, with Linux 6.8.0-52-generic (recovery mode)  ← SELECT THIS, press Enter
```

### Step 5.3: Drop to Root Shell

A **blue text recovery menu** appears with options:
```
resume          Resume normal boot
clean           Try to make free space
dpkg            Repair broken packages
fsck            Check all file systems
grub            Update GRUB bootloader
network         Enable networking
root            Drop to root shell prompt        ← SELECT THIS, press Enter
```

### Step 5.4: Reset Password

At the root shell (`root@fnetX:~#`):

```bash
mount -o remount,rw /
passwd friasc
# Type new password twice
reboot
```

**CRITICAL:** If the filesystem is read-only (default in recovery), `passwd` will fail with "Authentication token manipulation error". **The `mount -o remount,rw /` command is mandatory.**

After reboot, SSH login with known password:
```bash
ssh friasc@fnet2
```

---

## Part 6: Evidence Log

### Infrastructure Still Active (Non-Critical Context)

Even though USB autoinstall proved to be the working path for fnet2, the following infrastructure was built in parallel and remains operational:

#### PXE Server on fnet1 (dnsmasq)
- Config: `/etc/dnsmasq.d/pxe-lab.conf`
- Mode: **DHCP proxy** (does not conflict with TP-Link router)
- TFTP root: `/srv/tftp/`
- Files: `shimx64.efi`, `grubx64.efi`, `pxelinux.0`, `/ubuntu-24.04/vmlinuz`, `/ubuntu-24.04/initrd`
- Status: Configured and active. Works with standard Intel Boot Agent; **unreliable with Realtek/consumer PXE ROMs** (ASUS 2018 AMI BIOS timed out even when dnsmasq received broadcasts).
- Future use: May work on fnet3-fnet7 which have Intel NICs. Test per-node if PXE boot is desired.

#### WireGuard VPN
- Server: fnet1 (`wg0`, `10.200.200.1/24`)
- Client config: `/usr/local/etc/wireguard/wg0.conf` (orchestrator)
- DuckDNS: `carlos-lab.duckdns.org`
- Status: Active. Off-premises access deferred due to consumer router UDP port-forwarding issues (AT&T gateway + TP-Link unreliable for UDP).
- Future: Revisit when dedicated firewall (OPNsense/Protectli) replaces consumer router stack.

### Failures and Root Causes

| # | Symptom | Root Cause | Fix | Evidence |
|---|---------|-----------|-----|----------|
| 1 | Language screen / blue installer | GRUB discarded `s=http://...` via semicolon parsing | Quote the `ds=` parameter: `"ds=nocloud-net;s=..."` | AskUbuntu accepted answer, verified |
| 2 | "An error occurred" / installer hang | User `friasc` had no known password; placeholder hash was used without recording plaintext | Recovery mode password reset (Part 2A prevents this) | Ubuntu wiki RecoveryMode docs |
| 3 | Initramfs error after boot | USB disconnected mid-process or initrd corruption | Rewrote USB with verified ISO | XORRISO boot record check |
| 4 | Installer crashed immediately | Multi-disk explicit LVM config crashed Subiquity | Use `storage: {layout: {name: lvm, match: ...}}` | fnet1 HTTP logs (1s crash after fetch) |
| 5 | User cannot `sudo` or log in after install | Unknown password placeholder in autoinstall `identity.password` | Generate hash from plaintext and communicate it (Part 2A) | fnet2 incident report

### Historical Lessons (From fnet2 Journey, 2026-04-29–30)

| # | Lesson | Context |
|---|--------|---------|
| 6 | **Consumer PXE ROMs are unreliable** | ASUS 2018 AMI BIOS Realtek PXE timed out despite dnsmasq receiving broadcasts. PXE works with Intel Boot Agent (server boards) but fails on consumer desktop boards. |
| 7 | **DNSMASQ proxy mode hears but may not offer bootfile** for some PXE clients | Logs showed "vendor class received" for fnet2 but never "sent filename to 192.168.0.142". Suspected Realtek PXE ROM/dnsmasq incompatibility. |
| 8 | **Always keep ISO source cached locally** | Downloaded ISO twice due to temp file deletion overnight. Now persisted at `~/Downloads/binaries/`. |
| 9 | **fnet1 is not 100% stable** | Went offline mid-install (~22:30), returned ~6:22 next morning. Unknown cause (possibly dnsmasq restart loop). |
| 10 | **fnet6 is a reliable fallback server** | Ubuntu 22.04, 227GB free, python3 available. Temporarily hosted autoinstall HTTP server on port 8081 when fnet1 was down. |

### Verified Boot Command (Evidence)

```grub
linux /casper/vmlinuz autoinstall "ds=nocloud-net;s=http://192.168.0.141:8081/" cloud-config-url=/dev/null ---
```

- `autoinstall`: triggers unattended mode (verified by Ubuntu Server docs)
- `ds=nocloud-net;...`: tells cloud-init to fetch from HTTP, not AWS/Azure/etc.
- **quotes**: prevent GRUB from treating `;` as a statement separator
- `cloud-config-url=/dev/null`: prevents hang waiting for cloud metadata
- `---`: separates kernel params from initrd params (standard grub convention)

---

## Files Reference

| File | Location | Purpose |
|------|----------|---------|
| Source ISO | `~/Downloads/binaries/ubuntu-24.04.4-live-server-amd64.iso` | Canonical ISO (persisted for reuse) |
| Modified ISO | `/tmp/ubuntu-24.04.4-autoinstall-fixed.iso` | Hardcoded autoinstall (quoted ds=) |
| grub template | `/tmp/grub-corrected.cfg` | Correct bootloader config |
| user-data | `/tmp/fnet2-reimage/user-data` | Cloud-init autoinstall YAML |
| meta-data | `/tmp/fnet2-reimage/meta-data` | Cloud-init metadata |
| **This prompt** | `.pi/prompts/ubuntu-autoinstall-lab-nodes.md` | This document |

---

## Routing Notes

- `reasoning` (cloud): For analysis, planning, and decomposition
- `infrastructure` (local qwen3:8b): For status checks, SSH commands, live verification
- `structured` (local gemma4:e4b): For log parsing, file operations
- Domain: `technical-infrastructure`

---

**End of prompt.**
