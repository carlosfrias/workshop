# Sub-Task 27: Verify Connectivity Post-Fix

## Instruction

Execute a ping test to 8.8.8.8 to verify that internet connectivity has been restored after the driver fix.

## Command to Execute

```bash
ping -c 3 8.8.8.8
```

## Expected Output Format

```json
{
  "task": "fix_verify_ping",
  "step": 6,
  "success": true,
  "packets_sent": 3,
  "packets_received": 3,
  "packet_loss_percent": 0,
  "raw_output": "PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.\n64 bytes from 8.8.8.8: icmp_seq=1 ttl=117 time=15.2 ms\n64 bytes from 8.8.8.8: icmp_seq=2 ttl=117 time=14.8 ms\n64 bytes from 8.8.8.8: icmp_seq=3 ttl=117 time=15.1 ms\n\n--- 8.8.8.8 ping statistics ---\n3 packets transmitted, 3 received, 0% packet loss, time 2003ms",
  "exit_code": 0
}
```

## Verification Criteria

- [ ] `success` is boolean (true if any replies received)
- [ ] `packet_loss_percent` is a number (0-100)
- [ ] `raw_output` contains the actual ping output
- [ ] `exit_code` is 0 (success) or non-zero (failure)
- [ ] `step` is 6 (verification step)
- [ ] JSON is valid and parseable

## Example: Success (Fix Worked)

```json
{
  "task": "fix_verify_ping",
  "step": 6,
  "success": true,
  "packets_sent": 3,
  "packets_received": 3,
  "packet_loss_percent": 0,
  "raw_output": "PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.\n64 bytes from 8.8.8.8: icmp_seq=1 ttl=117 time=15.2 ms\n...\n\n--- 8.8.8.8 ping statistics ---\n3 packets transmitted, 3 received, 0% packet loss, time 2003ms",
  "exit_code": 0
}
```

## Example: Failure (Fix Did Not Work)

```json
{
  "task": "fix_verify_ping",
  "step": 6,
  "success": false,
  "packets_sent": 3,
  "packets_received": 0,
  "packet_loss_percent": 100,
  "raw_output": "PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.\n\n--- 8.8.8.8 ping statistics ---\n3 packets transmitted, 0 received, 100% packet loss, time 2047ms",
  "exit_code": 1
}
```

## Notes

- This is the verification step — compare with Sub-Task 6 (pre-fix ping)
- If this succeeds but Sub-Task 6 failed, the fix worked
- If this also fails, the fix did not work or another issue is present
