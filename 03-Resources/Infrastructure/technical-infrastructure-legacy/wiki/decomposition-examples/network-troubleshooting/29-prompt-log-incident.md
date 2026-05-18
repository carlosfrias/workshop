# Sub-Task 29: Log Incident to Wiki

## Instruction

Create a markdown file documenting this network troubleshooting incident. Write to the resume-work directory with a timestamped filename.

## Input

- All results from Sub-Tasks 3-28
- Current timestamp (America/New_York timezone)
- Node identifier (ask user, e.g., "fnet2", "node1")

## File to Create

```
./technical-infrastructure/resume-work/network-troubleshooting-<YYYY-MM-DD>-<node_id>.md
```

Example: `./technical-infrastructure/resume-work/network-troubleshooting-2026-04-24-fnet2.md`

## Expected Output Format

```json
{
  "task": "log_incident",
  "log_file": "./technical-infrastructure/resume-work/network-troubleshooting-2026-04-24-fnet2.md",
  "file_created": true,
  "incident_id": "2026-04-24-fnet2",
  "summary": {
    "node": "fnet2",
    "root_cause": "r8169 driver loaded instead of r8168-dkms",
    "resolution": "Installed r8168-dkms, switched drivers, restarted NetworkManager",
    "connectivity_restored": true
  },
  "follow_up_actions": {
    "blacklist_r8169": "pending",
    "update_initramfs": "pending",
    "pin_package": "pending",
    "dhcp_reservation": "pending"
  }
}
```

## Verification Criteria

- [ ] `log_file` path follows the naming convention
- [ ] `file_created` is boolean (true if file was written successfully)
- [ ] `incident_id` is unique (date + node identifier)
- [ ] `summary` includes node, root_cause, resolution, and connectivity_restored
- [ ] `follow_up_actions` includes all 4 hardening steps with status
- [ ] JSON is valid and parseable

## Markdown File Template

```markdown
# Network Troubleshooting Incident — fnet2

## Incident Metadata

| Field | Value |
|-------|-------|
| Date | 2026-04-24 |
| Time | 12:34:56 (America/New_York) |
| Node | fnet2 |
| Interface | enp7s0 |
| MAC Address | 0C:9D:92:CC:55:4C |
| Chipset | Realtek RTL8168H |

## Symptoms

- [x] Can ping gateway: YES (0% loss)
- [ ] Can ping 8.8.8.8: NO (100% loss) — **BEFORE FIX**
- [ ] DNS resolution works: NO
- [x] Packets observed leaving: YES (tcpdump: outbound_only pattern)
- [ ] Firewall blocking: NO

## Root Cause

r8169 driver loaded instead of r8168-dkms after kernel upgrade. The r8169 driver produces packets that the router silently drops.

## Resolution

1. Installed r8168-dkms package
2. Unloaded r8169 driver
3. Loaded r8168 driver
4. Restarted NetworkManager
5. Verified connectivity: ping 8.8.8.8 now succeeds (0% loss)

## Verification

- [x] Post-fix ping to 8.8.8.8: SUCCESS
- [x] Packet loss: 0%
- [x] Latency (avg): 15ms

## Follow-Up Actions

- [ ] Blacklist r8169: `echo "blacklist r8169" | sudo tee /etc/modprobe.d/blacklist-r8169.conf`
- [ ] Update initramfs: `sudo update-initramfs -u`
- [ ] Pin r8168-dkms package: `sudo apt-mark hold r8168-dkms`
- [ ] Add DHCP reservation on router for MAC 0C:9D:92:CC:55:4C

## Related Documentation

- Playbook: `./technical-infrastructure/prompts/network-troubleshooting.md`
- Decomposition: `./technical-infrastructure/wiki/decomposition-examples/network-troubleshooting/`
```

## Notes

- Create the parent directory if it doesn't exist
- Use the actual values from the diagnostic sub-tasks
- Mark follow-up actions as "pending" — user must complete them manually
