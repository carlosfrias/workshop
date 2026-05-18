# Sub-Task 15: Capture Packets with tcpdump

## Instruction

Run tcpdump to capture ICMP packets for 5 seconds. Return the RAW output only — analysis will be done in Sub-Task 16.

## Input

- Interface name from Sub-Task 10 (e.g., `enp7s0`)

## Commands to Execute

```bash
# Start tcpdump in background
sudo timeout 5 tcpdump -i <interface> icmp -c 20 &

# In parallel, send a ping
ping -c 2 8.8.8.8 > /dev/null 2>&1

# Wait for tcpdump to complete
sleep 6
```

## Expected Output Format

```json
{
  "task": "tcpdump_capture",
  "interface": "enp7s0",
  "raw_output": "<exact output from tcpdump>",
  "exit_code": 0
}
```

## Verification Criteria

- [ ] `raw_output` contains tcpdump lines (or error message)
- [ ] `exit_code` is 0 (success) or non-zero (failure)
- [ ] No analysis or counting — just capture
- [ ] JSON is valid and parseable

## Example: Packets Captured

```json
{
  "task": "tcpdump_capture",
  "interface": "enp7s0",
  "raw_output": "tcpdump: verbose output complete, data link type EN10MB (Ethernet)\n12:34:56.789012 IP 192.168.0.105 > 8.8.8.8: ICMP echo request, id 1234, seq 1, length 64\n12:34:56.792345 IP 8.8.8.8 > 192.168.0.105: ICMP echo reply, id 1234, seq 1, length 64\n12:34:57.789012 IP 192.168.0.105 > 8.8.8.8: ICMP echo request, id 1234, seq 2, length 64",
  "exit_code": 0
}
```

## Example: Permission Denied

```json
{
  "task": "tcpdump_capture",
  "interface": "enp7s0",
  "raw_output": "tcpdump: enp7s0: You don't have permission to capture on this device",
  "exit_code": 1
}
```

## Notes

- tcpdump requires sudo or membership in `wireshark` group
- Do NOT analyze the output — just capture it
- Analysis (counting outbound vs inbound) is Sub-Task 16
