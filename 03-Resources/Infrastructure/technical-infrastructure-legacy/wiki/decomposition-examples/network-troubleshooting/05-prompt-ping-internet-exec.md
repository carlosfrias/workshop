# Sub-Task 5: Execute Internet Ping (8.8.8.8)

## Instruction

Execute a ping command to Google's public DNS server (8.8.8.8) and return the RAW output only. Do NOT parse or interpret the results — that will be done in Sub-Task 6.

## Command to Execute

```bash
ping -c 3 8.8.8.8
```

## Expected Output Format

```json
{
  "task": "ping_internet_exec",
  "target": "8.8.8.8",
  "raw_output": "<exact output from ping command>",
  "exit_code": 0
}
```

## Verification Criteria

- [ ] `raw_output` contains the actual ping command output
- [ ] `exit_code` is 0 (success) or non-zero (failure)
- [ ] No interpretation or parsing of results
- [ ] JSON is valid and parseable

## Example: Success

```json
{
  "task": "ping_internet_exec",
  "target": "8.8.8.8",
  "raw_output": "PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.\n64 bytes from 8.8.8.8: icmp_seq=1 ttl=117 time=15.2 ms\n...\n\n--- 8.8.8.8 ping statistics ---\n3 packets transmitted, 3 received, 0% packet loss, time 2003ms",
  "exit_code": 0
}
```

## Example: Failure (Driver Issue Pattern)

```json
{
  "task": "ping_internet_exec",
  "target": "8.8.8.8",
  "raw_output": "PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.\n\n--- 8.8.8.8 ping statistics ---\n3 packets transmitted, 0 received, 100% packet loss, time 2047ms",
  "exit_code": 1
}
```

## Notes

- Do NOT parse the output — just capture it exactly
- Do NOT determine success/failure — that's Sub-Task 6
- This test uses IP address (not hostname) to isolate routing from DNS
