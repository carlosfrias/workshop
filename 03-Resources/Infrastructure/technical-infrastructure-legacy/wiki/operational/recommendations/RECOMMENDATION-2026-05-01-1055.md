# Recommendation: Disable Unattended-Upgrade Before Running Early-Boot Reconfiguration
**Date:** 2026-05-01 10:55  
**Context:** fnet1 early-boot LVM service triggered reboot, but Ubuntu's `unattended-upgrade` hooked the shutdown sequence and is running security updates before allowing the actual reboot. Machine shows "Unattended-upgrade in progress during shutdown" on physical console. Agent stalled because SSH dropped and can't reconnect until reboot completes.  
**Idea:** Before enabling any early-boot reconfiguration service that triggers reboot, disable `unattended-upgrade` temporarily:
```bash
sudo systemctl stop unattended-upgrades
sudo systemctl mask unattended-upgrades
# ... enable early-boot service, reboot ...
# After successful boot + verification:
sudo systemctl unmask unattended-upgrades
sudo systemctl start unattended-upgrades
```
**Reference:** See SESSION-NOTES-2026-05-01-0915.md fnet1 LVM rebuild section and decomposition-examples/systemd-mount-lock/05-prompt-pivot-to-early-boot.md.
